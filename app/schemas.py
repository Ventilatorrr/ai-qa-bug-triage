from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")

        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one number.")

        return password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class BugCreate(BaseModel):
    title: str
    affected_version: str | None = None
    description: str | None = None
    steps_to_reproduce: str | None = None
    expected_result: str | None = None
    actual_result: str | None = None
    severity: str | None = None
    priority: str | None = None
    assignee_id: int | None = None
    fix_version: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, title):
        if not title.strip():
            raise ValueError("Bug title is required.")
        return title
        
        