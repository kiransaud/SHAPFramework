from django.contrib.auth.models import AbstractUser
from django.db import models
from django_countries.fields import CountryField

class CustomUser(AbstractUser):
    name = models.CharField(blank=False, max_length=255)
    middle_name = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(blank=False, max_length=255)
    email = models.EmailField(unique=True)
    password= models.CharField(blank= False ,max_length=255)
    organization = models.CharField(blank=False, max_length=255)
    location = CountryField(blank=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'last_name']
    
class UserRoles(models.Model):
    DEVELOPER = 'DEV'
    QA_ENGINEER = 'QA'
    MANAGER = 'MGR'
    DOMAIN_EXPERT = 'DOM'

    ROLE_CHOICES = [
        (DEVELOPER, 'Developer'),
        (QA_ENGINEER, 'QA Engineer'),
        (MANAGER, 'Manager'),
        (DOMAIN_EXPERT, 'Domain Expert'),
    ]
    role = models.CharField(choices=ROLE_CHOICES,default=None, max_length=3)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_role')

    def __str__(self):
        return self.name + "-" + self.role



SCENARIO_CORRECT_DECISION = {
        1: "immediate",
        2: "algorithm",
        3: "scaling",
    }



# myapp/models.py

class StudySession(models.Model):
    """
    One participant’s session in an AB/BA (within‐subjects) design.
    - `order` determines which block (1–3 vs 4–6) is Baseline vs SHAP.
    - We store an AutoField `session_id` as the primary key.
    - `completed_at` and `total_time_ms` can be filled in later if desired.
    """
    ORDER_CHOICES = [
        ('A_first', 'Baseline first → then SHAP'),
        ('B_first', 'SHAP first → then Baseline'),
    ]

    session_id = models.AutoField(primary_key=True)
    order = models.CharField(
        max_length=10,
        choices=ORDER_CHOICES,
        help_text=(
            "A_first: scenarios 1–3 are Baseline (no SHAP) and 4–6 are SHAP.\n"
            "B_first: scenarios 1–3 are SHAP and 4–6 are Baseline."
        )
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_time_ms = models.BigIntegerField(null=True, blank=True)

    def _responses_by_block(self, baseline_block=True):
        """
        Return a QuerySet of ScenarioResponse rows that belong to
        either the Baseline block (if baseline_block=True) or SHAP block (False).
        """
        return self.responses.filter(is_baseline=baseline_block)

    def accuracy_baseline(self):
        """
        Of the three baseline‐mode scenarios, what fraction were marked correct?
        Returns None if fewer than 3 responses have been saved.
        """
        baseline_resps = list(self._responses_by_block(baseline_block=True))
        if len(baseline_resps) < 3:
            return None
        correct_count = sum(1 for r in baseline_resps if r.is_correct)
        return correct_count / 3.0

    def accuracy_shap(self):
        """
        Of the three SHAP‐mode scenarios, what fraction were correct?
        Returns None if fewer than 3 responses exist.
        """
        shap_resps = list(self._responses_by_block(baseline_block=False))
        if len(shap_resps) < 3:
            return None
        correct_count = sum(1 for r in shap_resps if r.is_correct)
        return correct_count / 3.0

    def accuracy_overall(self):
        """
        Fraction correct across all six scenarios (0.0–1.0), or None if fewer than 6.
        """
        all_resps = list(self.responses.all())
        if len(all_resps) < 6:
            return None
        correct_count = sum(1 for r in all_resps if r.is_correct)
        return correct_count / 6.0

    def __str__(self):
        return f"Session {self.session_id} ({self.order})"


class ScenarioResponse(models.Model):
    """
    One row per (session, scenario_number).  There will be exactly 6 rows per StudySession:
      - scenario_number: 1..6
      - decision_key: e.g. 'immediate', 'testing', 'scaling', etc.
      - confidence: integer 1..7
      - time_spent_ms: how long (in milliseconds) the user spent on this scenario
      - is_correct: automatically computed based on SCENARIO_CORRECT_DECISION
    """
    session = models.ForeignKey(
        StudySession,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    scenario_number = models.PositiveSmallIntegerField(
        help_text="1..6; 1–3 = first block, 4–6 = second block."
    )
    decision_key = models.CharField(
        max_length=50,
        help_text="Which choice the user clicked (e.g. 'immediate', 'algorithm', 'scaling', etc.)"
    )
    confidence = models.PositiveSmallIntegerField(
        help_text="User’s confidence rating (1=not confident … 7=very confident)."
    )
    time_spent_ms = models.BigIntegerField(
        help_text="Milliseconds elapsed from scenario display → submit."
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('session', 'scenario_number')
        ordering = ['session', 'scenario_number']

    def __str__(self):
        return f"Session {self.session.session_id} – Scenario {self.scenario_number}"

    @property
    def question_id(self):
        """
        Map each of the six scenario slots onto one of the three “questions”:
          • question 1 ← scenarios 1 & 4
          • question 2 ← scenarios 2 & 5
          • question 3 ← scenarios 3 & 6
        So if scenario_number > 3, subtract 3.
        """
        if self.scenario_number <= 3:
            return self.scenario_number
        return self.scenario_number - 3

    @property
    def is_baseline(self):
        """
        Return True if this particular scenario was in the Baseline block,
        False if it was in the SHAP block.

        Since we have an AB/BA counterbalance:
         - If session.order == 'A_first':  scenarios 1–3 were Baseline → return True for 1–3.
                                         scenarios 4–6 were SHAP     → return False for 4–6.
         - If session.order == 'B_first':  scenarios 1–3 were SHAP     → return False for 1–3.
                                         scenarios 4–6 were Baseline → return True for 4–6.
        """
        first_block_baseline = (self.session.order == 'A_first')
        if self.scenario_number <= 3:
            return first_block_baseline
        return not first_block_baseline

    def save(self, *args, **kwargs):
        """
        Before saving, compute `is_correct` by looking up the correct answer
        for this scenario’s question_id in SCENARIO_CORRECT_DECISION.
        """
        correct_answer = SCENARIO_CORRECT_DECISION.get(self.question_id)
        self.is_correct = (self.decision_key == correct_answer)
        super().save(*args, **kwargs)
