from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str



class TaskBase(BaseModel):
    title: str
    description: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)

class Task(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int

    

class TaskPermissionBase(BaseModel):
    user_id: int
    can_read: bool
    can_update: bool

class TaskPermissionCreate(TaskPermissionBase):
    pass

class TaskPermission(TaskPermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int

class TaskPermissionUpdate(BaseModel):
    can_update: bool | None = None
    can_read: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

