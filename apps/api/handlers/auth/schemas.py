from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    is_verified: bool = False


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthenticationResponse(TokenResponse):
    user: UserOut


class RegisterResponse(AuthenticationResponse):
    organization_id: str


class LogoutResponse(BaseModel):
    message: str


class OrganizationOut(BaseModel):
    id: str
    name: str
    slug: str
    owner_id: str
    role: str


class AuthContext(BaseModel):
    user_id: str
    email: EmailStr
    username: str
