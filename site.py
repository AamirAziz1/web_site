# -*- coding: utf-8 -*-
##############################################################################
#  COMPANY: BORN
#  AUTHOR: KIWI
#  EMAIL: arborous@gmail.com
#  VERSION : 1.0   NEW  2014/07/21
#  UPDATE : NONE
#  Copyright (C) 2011-2014 www.wevip.com All Rights Reserved
##############################################################################

from openerp.osv import fields, osv


class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        'db_name': fields.char(u'数据库名称', size=50),
        'web_http': fields.char(u'服务器地址', size=50),
        'contact_name': fields.char(u'联系人', size=50),
        'admin': fields.char(u'管理员名称', size=50, htlp=u"系统管理员名称不能修改，可以用于同步与密码修改"),
        'password': fields.char(u'管理员密码', size=50),
        'user_id': fields.many2one('res.users', u'注册人编号'),
        'is_register': fields.boolean(u'是否网站注册', help=u"是否网站注册的商户"),
        'state': fields.selection(
            [('draft', u'草稿'), ('review', u'提交申请'), ('done', u'运行中'), ('sent', u'发送邮件'), ('cancel', u'关闭'), ], u'状态', ),
        'born_uuid': fields.char(u'校验码', size=255, help=u"校验码"),
        'admin_password': fields.char(u'管理员密匙', size=255, help=u"管理员密匙"),
        'email_active_key': fields.char(u'激活验证码', size=255, help=u"激活验证码"),
        'brand': fields.char(u'品牌', size=255, help=u"品牌"),
        'employee_id': fields.many2one('hr.employee', u'技术', ),
        'sale_employee_id': fields.many2one('hr.employee', u'销售', ),
        'approve_date': fields.date(u'审核日期'),
        'is_ipad': fields.boolean(u'是否允许使用PAD MENU', help=u"是否允许使用PAD MENU"),
        'version_id': fields.many2one('born.version', u'版本'),
        'groups_ids': fields.many2many('born.version.groups', 'company_groups_rel', 'company_id', 'groups_id', u'功能'),
    }

    _defaults = {
        'is_register': False,
        'state': 'draft',
        'is_ipad': False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        # 修改扩展权限

        ret = super(res_company, self).write(cr, uid, ids, vals, context=context)
        if vals.has_key('version_id'):
            version = self.pool.get('born.version').browse(cr, uid, vals.get('version_id'), context)
            groups = [x.id for x in version.groups_ids]
            company = self.browse(cr, uid, ids, context)
            company_groups = [x.id for x in company.groups_ids]
            all_groups = list(set(groups).union(set(company_groups)))
            groups_ids = [(6, 0, all_groups)]
            self.write(cr, uid, ids, {'groups_ids': groups_ids}, context=context)
        return ret

    # 创建公司
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        company_id = super(res_company, self).create(cr, uid, vals, context=context)
        if vals.has_key('version_id'):
            version = self.pool.get('born.version').browse(cr, uid, vals.get('version_id'), context)
            groups = [x.id for x in version.groups_ids]
            company = self.browse(cr, uid, company_id, context)
            company_groups = [x.id for x in company.groups_ids]
            all_groups = list(set(groups).union(set(company_groups)))
            groups_ids = [(6, 0, all_groups)]
            self.write(cr, uid, company_id, {'groups_ids': groups_ids}, context=context)

        return company_id


class res_users(osv.osv):
    _inherit = "res.users"
    _columns = {
        'is_register': fields.boolean(u'是否网站注册', help=u"是否网站注册的商户"),
        'approved': fields.selection([('unapproved', u'未审核'), ('approved', u'已审核'), ('rejected', u'已拒绝')], u'认证', ),
        'born_uuid': fields.char(u'UUID', size=255, help=u"UUID"),
        'email_active': fields.boolean(u'邮件是否激活', help=u"邮件是否激活"),
    }
    _defaults = {
        'is_register': False,
        'email_active': False,
    }

# 权限
class born_version_groups(osv.osv):
    _name = "born.version.groups"
    _description = u"权限"

    # 获取默认公司
    def _default_company_id(self, cr, uid, context=None):
        if not context.get('company_id', False):
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        else:
            company_id = context.get('company_id', False)
        return company_id

    _columns = {
        'name': fields.char(u'名称', required=True),
        'group_id': fields.char(u'编号', help=u"权限id", required=True),
        'company_id': fields.many2one('res.company', u'公司'),
        'note': fields.text(u'说明'),
    }

    _defaults = {
        'company_id': _default_company_id,
    }


# 版本
class born_version(osv.osv):
    _name = "born.version"
    _description = u"版本"

    _columns = {
        'name': fields.char(u'名称', required=True),
        'note': fields.text(u'说明'),
        'template_id': fields.many2one('born.template.db', u'模板数据库', select=True),
        'groups_ids': fields.many2many('born.version.groups', 'born_version_groups_rel', 'version_id', 'group_id',
                                       u'权限'),
    }


# 模板数据库
class born_template_db(osv.osv):
    _name = "born.template.db"
    _description = u"默认数据库"

    _columns = {
        'name': fields.char(u'名称', required=True),
        'password': fields.char(u'密码', required=True),
        'url': fields.char(u'地址', required=True),
    }

#首页下载url
class born_download_url(osv.osv):
    _name = "born.download.url"
    _description = u"软件下载url列表"

    _columns = {
        'name' : fields.selection([('dianshang', u'店尚'), ('weika', u'微卡'), ('padmenu', u'电子菜单')], u'名称', ),
        'type' : fields.selection([('windows', u'Windows版'), ('ipad', u'iPad版'), ('iphone', u'iPhone版'),('android', u'Android版')], u'类型', ),
        'url' : fields.char(u'url',required=True),
    }


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'is_investment': fields.boolean(u'是否是官网招商用户')
    }