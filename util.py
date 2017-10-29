from WindPy import *
from config import *

def position_parser(wind_res):
    res = dict()
    for i, field in enumerate(wind_res.Fields):
        res[field] = wind_res.Data[i]
    return res


def start():
    w.start()
    w.tlogon(BrokerID=BrokerID,
             DepartmentID=DepartmentID,
             LogonAccount=LogonAccount,
             Password=Password,
             AccountType=AccountType
             )