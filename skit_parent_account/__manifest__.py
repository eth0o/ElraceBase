{
    "name": "skit_parent_account",
    'version': '14.0.1.0.0',
    "category": "Accounting",
    "license": "OPL-1",
    "summary": "Parent Account Hierarchy",
    "author": "Srikesh Infotech",
    "website": "www.srikeshinfotech.com",
    "depends": ['account'],
    "data": ['security/ir.model.access.csv',
             'views/account.xml',
             'wizard/account_hierarchy.xml',
             'views/parent_account_report.xml',
             'views/parent_account.xml',

             ],
    'assets': {
    },
    "installable": True,
    'auto_install': False,
    'application': True,
}
