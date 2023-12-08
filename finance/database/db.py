from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from django.conf import settings


finance = settings.DATABASES["financeApp"]


engine = create_engine(
    f"""mysql+mysqlconnector://{finance["USER"]}:{finance["PASSWORD"]}@{finance["HOST"]}:{finance["PORT"]}/{finance["NAME"]}""",
)
Session = sessionmaker(bind=engine)
