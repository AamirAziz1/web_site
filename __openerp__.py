# -*- coding: utf-8 -*-
##############################################################################
#  COMPANY: BORN
#  AUTHOR: KIWI
#  EMAIL: arborous@gmail.com
#  VERSION : 1.0   NEW  2014/07/21
#  UPDATE : NONE
#  Copyright (C) 2011-2014 www.wevip.com All Rights Reserved
##############################################################################

{
    'name': "官网",
    'author': '上海波恩网络科技服务有限公司',  # 作者
    'summary': 'BORN',
    'description': """
                     网站
     """,
    'category': 'BORN',
    'sequence': 8,
    'website': 'http://www.wevip.com',
    'images': [],
    'depends': ['base', 'mail', 'hr', 'born_odoo', 'born_sms'],

    'demo': [],
    'init_xml': [],
    'data': [
        'wizard/duplicate_database.xml',
        'wizard/control_panel.xml',
        'site_view.xml',
        'sequence.xml',
        'security/ir.model.access.csv',
        'data/site_data.xml',
        'data/groups_data.xml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
}
