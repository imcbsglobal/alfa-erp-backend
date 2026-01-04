"""
Management command to create store users with specific roles
Similar to createsuperuser but allows selecting operational roles
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from apps.accounts.models import User, Department, JobTitle
import getpass


class Command(BaseCommand):
    help = 'Create a store user with a specific role (PICKER, PACKER, DRIVER, DELIVERY, BILLING, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the user',
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=[choice[0] for choice in User.Role.choices],
            help='Role for the user',
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Full name of the user',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Create user without prompts (requires --email, --role, and password via env)',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        role = options.get('role')
        name = options.get('name')
        noinput = options.get('noinput')

        if noinput:
            if not email or not role:
                raise CommandError('--email and --role are required when using --noinput')
            password = None  # You'd typically get this from environment in automated scripts
        else:
            # Interactive prompts
            if not email:
                email = self.prompt_email()
            else:
                self.validate_email_input(email)

            if not role:
                role = self.prompt_role()

            if not name:
                name = input('Name (optional, press Enter to skip): ').strip()

            password = self.prompt_password()

        # Additional fields
        department_id = None
        job_title_id = None

        if not noinput:
            if self.confirm('Do you want to assign a department?'):
                department_id = self.select_department()

            if self.confirm('Do you want to assign a job title?'):
                job_title_id = self.select_job_title()

        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                name=name or '',
                role=role,
                department_id=department_id,
                job_title_id=job_title_id,
                is_active=True,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully created user:\n'
                    f'  Email: {user.email}\n'
                    f'  Role: {user.get_role_display()}\n'
                    f'  Name: {user.name or "(not set)"}\n'
                    f'  Department: {user.department.name if user.department else "(none)"}\n'
                    f'  Job Title: {user.job_title.title if user.job_title else "(none)"}'
                )
            )

        except IntegrityError:
            raise CommandError(f'User with email "{email}" already exists')
        except Exception as e:
            raise CommandError(f'Error creating user: {str(e)}')

    def prompt_email(self):
        """Prompt for and validate email"""
        while True:
            email = input('Email address: ').strip()
            try:
                self.validate_email_input(email)
                return email
            except CommandError as e:
                self.stdout.write(self.style.ERROR(str(e)))

    def validate_email_input(self, email):
        """Validate email format"""
        if not email:
            raise CommandError('Email cannot be empty')
        try:
            validate_email(email)
        except ValidationError:
            raise CommandError('Invalid email format')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email "{email}" already exists')

    def prompt_role(self):
        """Prompt for role selection"""
        self.stdout.write('\nAvailable roles:')
        roles = list(User.Role.choices)
        for idx, (value, label) in enumerate(roles, 1):
            self.stdout.write(f'  {idx}. {label} ({value})')

        while True:
            try:
                choice = input(f'\nSelect role (1-{len(roles)}): ').strip()
                idx = int(choice) - 1
                if 0 <= idx < len(roles):
                    return roles[idx][0]
                else:
                    self.stdout.write(self.style.ERROR(f'Please enter a number between 1 and {len(roles)}'))
            except (ValueError, IndexError):
                self.stdout.write(self.style.ERROR('Invalid input. Please enter a number.'))

    def prompt_password(self):
        """Prompt for password (hidden input)"""
        while True:
            password = getpass.getpass('Password: ')
            if not password:
                self.stdout.write(self.style.ERROR('Password cannot be empty'))
                continue

            password2 = getpass.getpass('Password (again): ')
            if password != password2:
                self.stdout.write(self.style.ERROR('Passwords do not match. Try again.'))
                continue

            # if len(password) < 6:
            #     self.stdout.write(self.style.ERROR('Password must be at least 8 characters'))
            #     continue

            return password

    def confirm(self, question):
        """Prompt yes/no question"""
        answer = input(f'{question} (y/N): ').strip().lower()
        return answer in ['y', 'yes']

    def select_department(self):
        """Select department from list"""
        departments = list(Department.objects.filter(is_active=True).order_by('name'))
        if not departments:
            self.stdout.write(self.style.WARNING('No departments available'))
            return None

        self.stdout.write('\nAvailable departments:')
        for idx, dept in enumerate(departments, 1):
            self.stdout.write(f'  {idx}. {dept.name}')

        while True:
            try:
                choice = input(f'Select department (1-{len(departments)}, or press Enter to skip): ').strip()
                if not choice:
                    return None
                idx = int(choice) - 1
                if 0 <= idx < len(departments):
                    return departments[idx].id
                else:
                    self.stdout.write(self.style.ERROR(f'Please enter a number between 1 and {len(departments)}'))
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid input. Please enter a number.'))

    def select_job_title(self):
        """Select job title from list"""
        job_titles = list(JobTitle.objects.filter(is_active=True).select_related('department').order_by('title'))
        if not job_titles:
            self.stdout.write(self.style.WARNING('No job titles available'))
            return None

        self.stdout.write('\nAvailable job titles:')
        for idx, jt in enumerate(job_titles, 1):
            dept_name = f' ({jt.department.name})' if jt.department else ''
            self.stdout.write(f'  {idx}. {jt.title}{dept_name}')

        while True:
            try:
                choice = input(f'Select job title (1-{len(job_titles)}, or press Enter to skip): ').strip()
                if not choice:
                    return None
                idx = int(choice) - 1
                if 0 <= idx < len(job_titles):
                    return job_titles[idx].id
                else:
                    self.stdout.write(self.style.ERROR(f'Please enter a number between 1 and {len(job_titles)}'))
            except ValueError:
                self.stdout.write(self.style.ERROR('Invalid input. Please enter a number.'))
