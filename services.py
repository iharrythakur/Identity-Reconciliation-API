from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import Contact, LinkPrecedence
from typing import List, Set, Tuple, Optional
from datetime import datetime


class IdentityService:
    def __init__(self, db: Session):
        self.db = db

    def identify_contact(self, email: Optional[str] = None, phone_number: Optional[str] = None) -> dict:
        """
        Main method to identify and reconcile contact identities
        """
        if not email and not phone_number:
            raise ValueError(
                "At least one of email or phoneNumber must be provided")

        # Find existing contacts that match the provided identifiers
        matching_contacts = self._find_matching_contacts(email, phone_number)

        if not matching_contacts:
            # No matches found, create new primary contact
            return self._create_new_primary_contact(email, phone_number)

        # Find the primary contact among matching contacts
        primary_contact = self._find_primary_contact(matching_contacts)

        # Get all linked contacts (primary + secondary)
        all_linked_contacts = self._get_all_linked_contacts(primary_contact.id)

        # Check if we need to add new identifiers
        new_identifiers = self._check_new_identifiers(
            all_linked_contacts, email, phone_number)

        if new_identifiers:
            # Add new secondary contact with new identifiers
            self._add_secondary_contact(primary_contact.id, new_identifiers.get(
                'email'), new_identifiers.get('phone_number'))
            # Refresh linked contacts after adding new one
            all_linked_contacts = self._get_all_linked_contacts(
                primary_contact.id)

        return self._build_response(all_linked_contacts)

    def _find_matching_contacts(self, email: Optional[str], phone_number: Optional[str]) -> List[Contact]:
        """Find contacts that match the provided email or phone number"""
        conditions = []
        if email:
            conditions.append(Contact.email == email)
        if phone_number:
            conditions.append(Contact.phoneNumber == phone_number)

        return self.db.query(Contact).filter(
            and_(
                or_(*conditions),
                Contact.deletedAt.is_(None)
            )
        ).all()

    def _find_primary_contact(self, contacts: List[Contact]) -> Contact:
        """Find the primary contact among a list of contacts"""
        primary_contacts = [
            c for c in contacts if c.linkPrecedence == LinkPrecedence.PRIMARY]

        if not primary_contacts:
            # If no primary contacts found, find the oldest contact and make it primary
            oldest_contact = min(contacts, key=lambda x: x.createdAt)
            oldest_contact.linkPrecedence = LinkPrecedence.PRIMARY
            oldest_contact.linkedId = None
            self.db.commit()
            return oldest_contact

        if len(primary_contacts) > 1:
            # Multiple primary contacts found, need to consolidate
            return self._consolidate_primary_contacts(primary_contacts)

        return primary_contacts[0]

    def _consolidate_primary_contacts(self, primary_contacts: List[Contact]) -> Contact:
        """Consolidate multiple primary contacts into one"""
        # Sort by creation time to find the oldest
        sorted_contacts = sorted(primary_contacts, key=lambda x: x.createdAt)
        oldest_primary = sorted_contacts[0]

        # Convert all other primary contacts to secondary
        for contact in sorted_contacts[1:]:
            contact.linkPrecedence = LinkPrecedence.SECONDARY
            contact.linkedId = oldest_primary.id
            contact.updatedAt = datetime.utcnow()

        self.db.commit()
        return oldest_primary

    def _get_all_linked_contacts(self, primary_id: int) -> List[Contact]:
        """Get all contacts linked to a primary contact"""
        return self.db.query(Contact).filter(
            and_(
                or_(
                    Contact.id == primary_id,
                    Contact.linkedId == primary_id
                ),
                Contact.deletedAt.is_(None)
            )
        ).all()

    def _check_new_identifiers(self, linked_contacts: List[Contact], email: Optional[str], phone_number: Optional[str]) -> Optional[dict]:
        """Check if the provided identifiers are new to the linked contacts"""
        existing_emails = {c.email for c in linked_contacts if c.email}
        existing_phones = {
            c.phoneNumber for c in linked_contacts if c.phoneNumber}

        new_identifiers = {}
        if email and email not in existing_emails:
            new_identifiers['email'] = email
        if phone_number and phone_number not in existing_phones:
            new_identifiers['phone_number'] = phone_number

        return new_identifiers if new_identifiers else None

    def _create_new_primary_contact(self, email: Optional[str], phone_number: Optional[str]) -> dict:
        """Create a new primary contact"""
        new_contact = Contact(
            email=email,
            phoneNumber=phone_number,
            linkPrecedence=LinkPrecedence.PRIMARY
        )
        self.db.add(new_contact)
        self.db.commit()
        self.db.refresh(new_contact)

        return self._build_response([new_contact])

    def _add_secondary_contact(self, primary_id: int, email: Optional[str], phone_number: Optional[str]) -> Contact:
        """Add a new secondary contact linked to the primary"""
        secondary_contact = Contact(
            email=email,
            phoneNumber=phone_number,
            linkedId=primary_id,
            linkPrecedence=LinkPrecedence.SECONDARY
        )
        self.db.add(secondary_contact)
        self.db.commit()
        self.db.refresh(secondary_contact)
        return secondary_contact

    def _build_response(self, contacts: List[Contact]) -> dict:
        """Build the response object from a list of contacts"""
        primary_contact = next(
            (c for c in contacts if c.linkPrecedence == LinkPrecedence.PRIMARY), None)
        if not primary_contact:
            raise ValueError("No primary contact found")

        # Collect all unique emails and phone numbers
        emails = list(set(c.email for c in contacts if c.email))
        phone_numbers = list(
            set(c.phoneNumber for c in contacts if c.phoneNumber))

        # Collect secondary contact IDs
        secondary_ids = [
            c.id for c in contacts if c.linkPrecedence == LinkPrecedence.SECONDARY]

        return {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_ids
        }
