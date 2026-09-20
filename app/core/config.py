from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    # URLs del frontend que pueden llamar a esta API (CORS). En local es
    # Vite (5173); en producción, agrega aquí la URL real que te dé Render
    # separando varias con comas si algún día hay más de un frontend, por
    # ejemplo: FRONTEND_URL=https://manosya.onrender.com
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def origenes_permitidos(self) -> list[str]:
        return [url.strip() for url in self.frontend_url.split(",") if url.strip()]


settings = Settings()
