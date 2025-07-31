from django.test import TestCase
from Frontend.models import CustomUser
from Frontend.forms import CustomUserCreationForm

class CustomUserCreationFormTest(TestCase):
    def setUp(self):
        # If 'location' is a ForeignKey or ChoiceField, adjust this value
        self.valid_data = {
            'name': 'John',
            'middle_name': 'H.',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'strongpass',
            'organization': 'Example Org',
            'location': 'NL',  # Ensure this is a valid value for your model.
        }

    def test_valid_form(self):
        """Test that the form is valid when provided with correct data."""
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Save and verify the user
        user = form.save()
        self.assertEqual(user.username, self.valid_data['email'])
        self.assertTrue(user.check_password(self.valid_data['password']))

    def test_missing_name(self):
        """Test that the form errors out when 'name' is missing."""
        data = self.valid_data.copy()
        data['name'] = ''
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_missing_last_name(self):
        """Test that the form errors out when 'last_name' is missing."""
        data = self.valid_data.copy()
        data['last_name'] = ''
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_invalid_email(self):
        """Test that the form errors out when an invalid email is provided."""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_email(self):
        """Test that the form errors when the email already exists."""
        # Create a user with the same email by supplying username explicitly.
        duplicate_data = self.valid_data.copy()
        duplicate_data['username'] = duplicate_data['email']
        CustomUser.objects.create_user(**duplicate_data)
        
        form = CustomUserCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn("Email already exists.", form.errors['email'][0])

    def test_password_length(self):
        """Test that a password shorter than 6 characters causes an error."""
        data = self.valid_data.copy()
        data['password'] = '123'
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        self.assertIn('at least 6', form.errors['password'][0].lower())

    def test_missing_organization(self):
        """Test that the form errors when 'organization' is missing."""
        data = self.valid_data.copy()
        data['organization'] = ''
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('organization', form.errors)

    def test_missing_location(self):
        """Test that the form errors when 'location' is missing."""
        data = self.valid_data.copy()
        data['location'] = ''
        form = CustomUserCreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('location', form.errors)
