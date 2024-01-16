# Copyright © Lumenore Inc. All rights reserved.
# This software is the confidential and proprietary information of
# Lumenore Inc. "Confidential Information".
# You shall * not disclose such Confidential Information and shall use it only in
# accordance with the terms of the intellectual property agreement
# you entered into with Lumenore Inc.
# THIS SOFTWARE IS INTENDED STRICTLY FOR USE BY Lumenore Inc.
# AND ITS PARENT AND/OR SUBSIDIARY COMPANIES. Lumenore
# MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
# Lumenore SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY ANY PARTY AS A RESULT
# OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

"""models"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Float, Boolean, func, text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class FnForm(Base):
    '''FnForm

    Args:
        Base (_type_):
    '''
    __tablename__ = 'fn_form'

    fn_form_id = Column(Integer, primary_key=True, autoincrement=True)
    form_name = Column(String(255))
    lum_user_id = Column(Integer, nullable=False)
    lum_org_id = Column(Integer, nullable=False)
    created_by = Column(Integer, nullable=False)
    modified_by = Column(Integer, nullable=False)
    created_on = Column(TIMESTAMP, server_default=func.now())
    modified_on = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=True)


class FnUserData(Base):
    '''FnUserData

    Args:
        Base (_type_):
    '''
    __tablename__ = 'fn_user_data'

    fn_user_data_id = Column(Integer, primary_key=True, autoincrement=True)
    fn_form_id = Column(Integer, ForeignKey('fn_form.fn_form_id'))
    date = Column(TIMESTAMP, server_default=func.now())
    receipt_number = Column(String(255))
    business_unit = Column(String(255))
    account_type = Column(String(255))
    account_subtype = Column(String(255))
    project_name = Column(String(255))
    customer_name = Column(String(255), default=None)
    amount_type = Column(String(255))
    amount = Column(Float)
    created_by = Column(Integer)
    modified_by = Column(Integer)
    created_on = Column(TIMESTAMP, server_default=func.now())
    modified_on = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())
    is_active = Column(Boolean, default=True)

    form = relationship("FnForm", backref="user_data")


class FnScenario(Base):
    '''FnScenario

    Args:
        Base (_type_):
    '''
    __tablename__ = 'fn_scenario'

    fn_scenario_id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_name = Column(String(255), default=None)
    scenario_description = Column(String(5000), default=None)
    fn_form_id = Column(Integer, ForeignKey('fn_form.fn_form_id'), nullable=False)
    created_on = Column(TIMESTAMP, server_default=func.now())
    modified_on = Column(TIMESTAMP, server_default=func.now(), server_onupdate=func.now())
    created_by = Column(Integer, nullable=False)
    modified_by = Column(Integer, nullable=False)
    is_draft = Column(Boolean, nullable=False, server_default=text("0"))
    is_active = Column(Boolean, nullable=False, default=True)

    form = relationship("FnForm", backref="scenarios")


class FnScenarioData(Base):
    '''FnScenarioData

    Args:
        Base (_type_):
    '''
    __tablename__ = 'fn_scenario_data'

    fn_scenario_data_id = Column(Integer, primary_key=True, autoincrement=True)
    fn_scenario_id = Column(Integer, ForeignKey('fn_scenario.fn_scenario_id'), nullable=False)
    date = Column(TIMESTAMP, server_default=func.now())
    receipt_number = Column(String(255), default=None)
    business_unit = Column(String(255), default=None)
    account_type = Column(String(255), default=None)
    account_subtype = Column(String(255), default=None)
    project_name = Column(String(255), default=None)
    customer_name = Column(String(255), default=None)
    amount_type = Column(Integer, default=None)
    amount = Column(Float, nullable=False)
    change_value = Column(Integer, nullable=False, default=0)
    created_by = Column(Integer, nullable=False)
    modified_by = Column(Integer, nullable=False)
    created_on = Column(TIMESTAMP, server_default=func.now())
    modified_on = Column(TIMESTAMP, server_default=func.now(),server_onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=True)

    scenario = relationship("FnScenario", backref="scenario_data")

class JwtSettings(Base):
    '''JwtSettings

    Args:
        Base (_type_):
    '''
    __tablename__ = 'jwt_settings'
    id = Column(Integer, primary_key=True)
    secret = Column(String)
    isActive = Column(Boolean)
    client_id = Column(String)
    organizationId = Column(Integer)
