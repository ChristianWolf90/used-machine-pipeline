from enum import Enum


class MachineStatus(str, Enum):
    UNDERWAY = 'UNDERWAY'
    INTAKE_ASSESSMENT = 'INTAKE_ASSESSMENT'
    REFURBISHMENT = 'REFURBISHMENT'
    SALE_READY = 'SALE_READY'


class ValueClass(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'


class RefurbSite(str, Enum):
    PASSAU = 'Passau'
    ANDERNACH = 'Andernach'
    WELZOW = 'Welzow'


class UserRole(str, Enum):
    ADMIN = 'Admin'
    SITE_USER = 'SiteUser'
