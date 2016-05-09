# # -*- coding:utf-8 -*-
import datetime
import json
import logging
from openerp import SUPERUSER_ID
import openerp
from openerp.addons.web import http
from openerp.http import request
import uuid
import base64
import StringIO
import random
from ..tools.generate import generate
import cStringIO
_logger = logging.getLogger(__name__)

MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)
from jinja2 import Environment, FileSystemLoader
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
path = os.path.join(BASE_DIR, "newTemplates")
templateLoader = FileSystemLoader(path)

env = Environment(loader=templateLoader)

#动态切换数据库
def ensure_db(db='big_white9.0-0.1',redirect='/except'):
    if not db:
        db = request.params.get('db')

    if db and db not in http.db_filter([db]):
        db = None
    if not db and request.session.db and http.db_filter([request.session.db]):
        db = request.session.db
    request.session.db = db

class Website(openerp.addons.web.controllers.main.Home):
    @http.route('/site/<path:path>', type='http', auth="none",)
    def site(self, **post):
        return http.local_redirect('/index', query=request.params, keep_hash=True)

    def _get_company(self):
        company = {'name':u'上海波恩网络科技服务有限公司'}
        return company

    #首页
    @http.route('/site/index', type='http', auth="none",)
    def home(self, **post):
        ensure_db()
        template = env.get_template('index.html')
        html = template.render(gituser='company')
        return html

    # #test------
    # @http.route('/site/<string:code>',type='http', auth="none",csrf=False)
    # def public_url(self,code,**post):
    #     _logger.info("----------------------------")
    #     template = env.get_template('%s.html'%code)
    #     html = template.render(gituser='company')
    #     return html

    @http.route('/site/register',type='http',auth="public",csrf=False)
    def register(self,**post):
        ensure_db()
        template = env.get_template('register.html')
        country_state_area_obj = request.registry['res.country.state.area']
        country_state_area_subdivide_obj = request.registry['res.country.state.area.subdivide']
        industry_obj = request.registry['born.industry']
        state_obj = request.registry.get('res.country.state')
        res =  request.registry.get('res.country').search(request.cr, SUPERUSER_ID, [('code','=','CN')], limit=1, context=request.context)

        #商户类型

        industry_categorys=[]
        country_state_areas=[]
        state_area_subdivides=[]

        #业务类型
        # if industrys:
        #     industry_id=industrys[0]['id']
        #     industry_categorys = industry_category_obj.search_read(request.cr, SUPERUSER_ID,[('industry_id','=',int(industry_id))],['id','name'], context=request.context)

        #odoo9.0  ----   行业分类
        industrys = industry_obj.search_read(request.cr, SUPERUSER_ID,[('parent_id','=',False),('active','=',True)],['id','name'], order='id asc',context=request.context)
        if industrys:
            industry_id=industrys[0]['id']
            industry_categorys = industry_obj.search_read(request.cr, SUPERUSER_ID,[('parent_id','=',int(industry_id)),('active','=',True)],['id','name'], context=request.context)

        #省市县
        country_id=res and res[0] or False
        states = state_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',country_id)],['id','name'], order='id asc',context=request.context)
        if states:
            country_id=states[0]['id']
            country_state_areas = country_state_area_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',int(country_id))],['id','name'], context=request.context)

        if country_state_areas:
            country_id=country_state_areas[0]['id']
            state_area_subdivides = country_state_area_subdivide_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',int(country_id))],['id','name'], context=request.context)

        gen =generate()
        image,str= gen.create_validate_code()
        jpeg_image_buffer = cStringIO.StringIO()
        image.save(jpeg_image_buffer, format="gif")
        image_stream = base64.b64encode(jpeg_image_buffer.getvalue())
        request.session.image_code=str
        html = template.render(industrys=industrys,industry_categorys=industry_categorys,states=states,country_state_areas=country_state_areas,state_area_subdivides=state_area_subdivides,image_stream=image_stream)
        return html

    @http.route('/site/register_mobile',type='http',auth="public",csrf=False)
    def register_mobile(self,**post):
        ensure_db()
        template = env.get_template('register_mobile.html')
        industry_obj = request.registry['born.industry']

        #商户类型
        industry_categorys=[]
        #odoo9.0  ----   行业分类
        industrys = industry_obj.search_read(request.cr, SUPERUSER_ID,[('parent_id','=',False),('active','=',True)],['id','name'], order='id asc',context=request.context)
        if industrys:
            industry_id=industrys[0]['id']
            industry_categorys = industry_obj.search_read(request.cr, SUPERUSER_ID,[('parent_id','=',int(industry_id)),('active','=',True)],['id','name'], context=request.context)

        gen =generate()
        image,str= gen.create_validate_code()
        jpeg_image_buffer = cStringIO.StringIO()
        image.save(jpeg_image_buffer, format="gif")
        image_stream = base64.b64encode(jpeg_image_buffer.getvalue())
        request.session.image_code=str
        html = template.render(gituser='company',industrys=industrys,industry_categorys=industry_categorys,image_stream=image_stream)
        return html

    @http.route('/site/json/get_industry_category', type='http', auth="none",csrf=False)
    def get_industry_category(self,industry_id=None, **kwargs):
        if industry_id:
            # industry_category_obj = request.registry.get('born.industry.category')
            industry_obj = request.registry['born.industry']
            data = industry_obj.search_read(request.cr, SUPERUSER_ID,[('parent_id','=',int(industry_id)),('active','=',True)],['id','name'], context=request.context)
            if data:
                json_industry_category = json.dumps(data,sort_keys=True)
                return  json_industry_category
        return None

    @http.route('/site/json/get_city', type='http', auth="none",csrf=False)
    def get_city(self,country_id=None, **kwargs):
        are_obj = request.registry.get('res.country.state.area')
        if country_id:
            data = are_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',int(country_id))],['id','name'], context=request.context)
            if data:
                json_city = json.dumps(data,sort_keys=True)
                return json_city
        return None

    @http.route('/site/json/get_subdivide', type='http', auth="none",csrf=False)
    def get_subdivide(self,states_id=None, **kwargs):
        subdivide_orm  = request.registry.get('res.country.state.area.subdivide')
        if states_id:
            model_data = subdivide_orm.search_read(request.cr, SUPERUSER_ID,[('country_id','=',int(states_id))],['id','name'], context=request.context)
            if model_data:
                json_subdivide = json.dumps(model_data,sort_keys=True)
                return json_subdivide
        return None;

    @http.route('/site/json/validate_email', type='http', auth="none",csrf=False)
    def validate_email(self,code=None,phone=None, **kwargs):
        user_obj = request.registry.get('res.users')
        sms_obj = request.registry.get('born.sms')
        result={}
        if phone and code:
            users = user_obj.search(request.cr, SUPERUSER_ID, [('login', '=', phone)], context=request.context)
            if users:
                result={'result':False ,'message':u'您输入的手机号码已经被使用' }
                return json.dumps(result,sort_keys=True)
            #验证验证码是否正确
            sms=sms_obj.search(request.cr, SUPERUSER_ID, [('phone', '=', phone),('security_code', '=', code),('state', '=', 'send')], context=request.context)
            if not sms:
                result={'result':False ,'message' :u'短信认证码错误'  }
                return json.dumps(result,sort_keys=True)
            else:
                result={'result':True }
                return json.dumps(result,sort_keys=True)
        return json.dumps({'result':False,'message' :u'验证码认证失败' },sort_keys=True)

    @http.route('/site/json/validate_company_name', type='http', auth="none",csrf=False)
    def validate_company_name(self,company_name=None, **kwargs):
        user_obj = request.registry.get('res.company')
        result={}
        if company_name:
            users = user_obj.search(request.cr, SUPERUSER_ID, [('name', '=', company_name)], context=request.context)
            if users:
                result={'result':False ,'message' :u'该公司名称已被注册！'}
                return json.dumps(result,sort_keys=True)
            else:
                result={'result':True }
                return json.dumps(result,sort_keys=True)
        return json.dumps({'result':False,'message' :u'公司名称查重失败'},sort_keys=True)

    @http.route('/site/signup', type='http', auth="none",methods=['POST'],csrf=False)
    def signup(self, **vals):

        is_alone= vals.get('is_alone','0'),
        is_alone=is_alone[0]

        if is_alone=='0':
            is_alone=True
        else:
            is_alone=False

        sms_obj = request.registry.get('born.sms')
        sms=sms_obj.search(request.cr, SUPERUSER_ID, [('phone', '=', vals.get('phone',False)),('security_code', '=', vals.get('code',False)),('state', 'in', ('send','finished'))], offset=0, limit=1, order=" id desc", context=request.context)
        sms_id= sms and sms[0] or False
        if not sms_id:
            return http.local_redirect('/site/index')

        res = request.registry.get('res.country').search(request.cr, SUPERUSER_ID, [('code', '=', 'CN')], context=request.context)
        country_id= res and res[0] or False

        email_active_key=str(uuid.uuid4())
        post = {
            'name': vals.get('company_name',False),
            'contact_name': vals.get('contact_name',False),
            'street':vals.get('street',False),
            'phone':vals.get('phone',False),
            'email':vals.get('email',False),
            'admin': vals.get('email',False),
            'brand':vals.get('brand',False),
            'born_uuid':str(uuid.uuid4()),
            'currency_id':8,
            'is_register':True,
            'is_alone':is_alone,
            'password': vals.get('password',0),
            'country_id':country_id,
            'state_id':vals.get('state_id',False),
            'area_id':vals.get('area_id',False),
            'subdivide_id':vals.get('subdivide_id',False),
            'business_id': int(vals.get('industry')) if vals.get('industry') else False,
            'sub_business_id': int(vals.get('industry_category')) if vals.get('industry_category') else False,
            'email_active_key':email_active_key,
        }

        company_id=request.registry['res.company'].create(request.cr, SUPERUSER_ID, post, request.context)

        #创建用户
        user_parm = {
            'company_id': company_id,
            'born_uuid':str(uuid.uuid4()),
            'login':vals.get('phone',False),
            'name': vals.get('contact_name',False),
            'company_ids': False,
            'active':True,
            'share':False,
            'is_register':True,
            'approved':'unapproved',
            'password': vals.get('password',0),
            'pp': vals.get('password',0),
        }
        user_id = request.registry['res.users'].create(request.cr, SUPERUSER_ID, user_parm, request.context)

        parm = {
            'phone':vals.get('phone',False),
            'email':vals.get('email',False),
            'admin':vals.get('email',False),
            'currency_id':8,
            'is_register':True,
            'password': vals.get('password',False),
            'user_id': user_id,
        }
        request.registry['res.company'].write(request.cr, SUPERUSER_ID, company_id, parm)

        # 读取公司生成的客户ID再次更新
        records = request.registry['res.company'].read(request.cr, SUPERUSER_ID, company_id, ['partner_id'])

        parm = {
            'email': vals.get('email',False),
            'born_uuid':str(uuid.uuid4()),
            'phone': vals.get('phone',False),
        }
        request.registry['res.partner'].write(request.cr, SUPERUSER_ID, records['partner_id'][0], parm)

        args={'param1':vals.get('company_name',False)}
        ret=sms_obj.send_message_for_call(request.cr, SUPERUSER_ID,vals.get('phone',False),'91005639',args,1,'', request.context)
        _logger.info(ret)

        try:
            #发送邮件
            tmpl_obj = request.registry['email.template']
            #发送通知邮件
            template_notice = request.registry['ir.model.data'].get_object(request.cr, SUPERUSER_ID, 'site', 'company_signup_notice_email')
            tmpl_obj.send_mail(request.cr, SUPERUSER_ID, template_notice.id, company_id, force_send=True, raise_exception=True)
        except:
            _logger.info(u'发送邮件失败%s' % (vals.get('company_name',False)))
            pass

        #获取需要发送消息的用户
        user_obj = request.registry['res.users']
        users = user_obj.search(request.cr, SUPERUSER_ID,[('role_option','=',1)], context=request.context)

        if users:
            #发送通知给管理员
            message=u"有新的公司在线注册了WE-ERP软件,公司名称：%s" % (vals.get('company_name',False))
            push_obj = request.registry['born.push']

            for user in users:
                vals_message={
                    'title':u'有新的公司注册',
                    'phone':vals.get('phone',''),
                    'content':message,
                    'type':'boss',
                    'state':'done',
                    'user_id':user,
                    'message_type':'1',
                }
                push_id = push_obj.create(request.cr, SUPERUSER_ID,vals_message,context=request.context)
                push_obj.send_message(request.cr, SUPERUSER_ID,push_id,context=request.context)

        return http.local_redirect('/site/success',keep_hash=True)

    @http.route('/site/success', type='http', auth="none",csrf=False)
    def success_message(self):
        template = env.get_template('success.html')

        html = template.render(title=u"注册成功",message=u"激活邮件已经发送到您的邮箱中，请及时激活。完成注册")
        return html

    @http.route('/site/account_active', type='http', auth="none",csrf=False)
    def account_active(self, email=None,key=None, **kwargs):

        user_obj = request.registry['res.users']
        template = env.get_template('success.html')
        if email and key:
            users = user_obj.search_read(request.cr, SUPERUSER_ID,[('login','=',email)], context=request.context)
            if users:
                user_id=users[0]['id']
                user = user_obj.browse(request.cr, SUPERUSER_ID, user_id,context=request.context)
                if user.email_active:
                    html = template.render(title=u"激活成功",message=u"您的帐号已经激活成功，请等待管理员审核。")
                    return html
                email_active_key=user.company_id.email_active_key
                if email_active_key==key:
                    parm = {
                        'email_active':True,
                    }
                    request.registry['res.users'].write(request.cr, SUPERUSER_ID, user_id, parm)
                    html = template.render(title=u"激活成功",message=u"您的帐号已经激活成功，请等待管理员审核。")
                    return html
        html = template.render(title=u"激活失败",message=u"无法激活您的账户，请联系管理员。")
        return html

    @http.route('/site/json/get_code', type='http', auth="none",csrf=False)
    def get_code(self,phone, **post):

        image_code=post.get('image_code','')
        if image_code.upper()!=request.session.image_code.upper():
            result={'result':False,'message':u"您输入正确的验证码。"}
            return json.dumps(result,sort_keys=True)

        sms_obj = request.registry.get('born.sms')
        user_obj = request.registry.get('res.users')
        result={}
        if phone:
            users = user_obj.search(request.cr, SUPERUSER_ID, [('login', '=', phone)], context=request.context)
            if users:
                result={'result':False,'message':u"您输入的手机号码已经被使用。"}
                return json.dumps(result,sort_keys=True)

        captcha= random.randint(100000, 999999)
        args={'param1':captcha}
        ret=sms_obj.send_message_for_call(request.cr, SUPERUSER_ID,phone,'91005638',args,1,captcha, request.context)
        _logger.info(ret)
        result={'result':True,'message':u"短信已经发送到您的手机，请注意查收。"}
        return json.dumps(result,sort_keys=True)


    ####################################################################################################################################



    @http.route('/site/default',type='http',auth="public",)
    def home1(self,**post):
        template = env.get_template('default.html')
        if request.session.uid != None:
            html = template.render(gituser=self._get_company(),)
            return html

        html = template.render(gituser=self._get_company())
        #html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/iepolicy',type='http',auth="public",)
    def iepolicy(self, **post):
        template = env.get_template('iepolicy.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/ieregister', type='http', auth="public",)
    def ieregister(self, **post):
        template = env.get_template('ieregister.html')

        #商户类型
        industry_obj = request.registry['born.industry']
        industry_category_obj = request.registry['born.industry.category']
        country_state_area_obj = request.registry['res.country.state.area']
        country_state_area_subdivide_obj = request.registry['res.country.state.area.subdivide']

        industrys = industry_obj.search_read(request.cr, SUPERUSER_ID,[],['id','name'], order='id asc',context=request.context)
        industry_categorys=[]
        country_state_areas=[]
        state_area_subdivides=[]

        #业务类型
        if industrys:
            industry_id=industrys[0]['id']
            industry_categorys = industry_category_obj.search_read(request.cr, SUPERUSER_ID,[('industry_id','=',int(industry_id))],['id','name'], context=request.context)

        #省市县
        state_obj = request.registry.get('res.country.state')
        res =  request.registry.get('res.country').search(request.cr, SUPERUSER_ID, [('code','=','CN')], limit=1, context=request.context)
        country_id=res and res[0] or False
        states = state_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',country_id)],['id','name'], order='id asc',context=request.context)
        if states:
            country_id=states[0]['id']
            country_state_areas = country_state_area_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',int(country_id))],['id','name'], context=request.context)

        if country_state_areas:
            country_id=country_state_areas[0]['id']
            state_area_subdivides = country_state_area_subdivide_obj.search_read(request.cr, SUPERUSER_ID,[('country_id','=',int(country_id))],['id','name'], context=request.context)

        html = template.render(industrys=industrys,industry_categorys=industry_categorys,states=states,country_state_areas=country_state_areas,state_area_subdivides=state_area_subdivides)
        return html


    @http.route('/site/json/image_code', type='http', auth="none")
    def image_code(self,name=None, **kwargs):
        user_obj = request.registry.get('res.company')
        result={}

        gen =generate()
        image,str= gen.create_validate_code()
        jpeg_image_buffer = cStringIO.StringIO()
        image.save(jpeg_image_buffer, format="gif")
        image_stream = base64.b64encode(jpeg_image_buffer.getvalue())
        request.session.image_code=str
        result={'image':image_stream }
        return json.dumps({'result':False  },sort_keys=True)


    #pos收银
    @http.route('/site/pos', type='http', auth="none",)
    def pos(self, **post):
        template = env.get_template('pos.html')
        html = template.render(gituser=self._get_company())
        return html

    #pos收银
    @http.route('/site/hardware', type='http', auth="none",)
    def hardware(self, **post):
        template = env.get_template('hardware.html')
        html = template.render(gituser=self._get_company())
        return html

    #pos收银
    @http.route('/site/marketing', type='http', auth="none",)
    def marketing(self, **post):
        template = env.get_template('marketing.html')
        html = template.render(gituser=self._get_company())
        return html


    #商业类型
    @http.route('/site/businesstype', type='http', auth="none",)
    def businesstype(self, **post):
        template = env.get_template('businesstype.html')
        html = template.render(gituser=self._get_company())
        return html


    #技术支持
    @http.route('/site/support', type='http', auth="none",)
    def support(self, **post):
        template = env.get_template('support.html')
        html = template.render(gituser=self._get_company())
        return html

    #活动
    @http.route('/site/active', type='http', auth="none",)
    def active(self, **post):
        template = env.get_template('active.html')
        html = template.render(gituser=self._get_company())
        return html

    #下载
    @http.route('/site/download', type='http', auth="public",)
    def download(self, **post):
        ensure_db()
        template = env.get_template('download.html')

        url_obj = request.registry['born.download.url']
        dianshang_windows = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','dianshang'),('type','=','windows')],['id','url'], order=" id desc",context=request.context) or [{'url': u'', 'id': 0}]
        dianshang_ipad = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','dianshang'),('type','=','ipad')],['id','url'],order=" id desc", context=request.context) or [{'url': u'', 'id': 0}]
        dianshang_iphone = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','dianshang'),('type','=','iphone')],['id','url'], order=" id desc",context=request.context) or [{'url': u'', 'id': 0}]
        dianshang_android = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','dianshang'),('type','=','android')],['id','url'], order=" id desc",context=request.context) or [{'url': u'', 'id': 0}]
        weika_android = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','weika'),('type','=','android')],['id','url'],order=" id desc", context=request.context) or [{'url': u'', 'id': 0}]
        weika_iphone = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','weika'),('type','=','windows')],['id','url'],order=" id desc", context=request.context) or [{'url': u'', 'id': 0}]
        padmenu_ipad = url_obj.search_read(request.cr, SUPERUSER_ID,[('name','=','padmenu'),('type','=','ipad')],['id','url'], order=" id desc",context=request.context) or [{'url': u'', 'id': 0}]
        html = template.render(gituser=self._get_company(),dianshang_windows=dianshang_windows,padmenu_ipad=padmenu_ipad,weika_iphone=weika_iphone,weika_android=weika_android,dianshang_android=dianshang_android,dianshang_iphone=dianshang_iphone,dianshang_ipad=dianshang_ipad)
        return html


    #微卡
    @http.route('/site/weika', type='http', auth="none",)
    def weika(self, **post):
        template = env.get_template('weika.html')
        html = template.render(gituser=self._get_company())
        return html


    @http.route('/site/padmenu',type='http',auth="none",)
    def padmenu(self,**post):
        template = env.get_template('padmenu.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/about',type='http',auth="none",)
    def about(self,**post):
        template = env.get_template('about.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/dianshang',type='http',auth="none",)
    def dianshang(self,**post):
        template = env.get_template('dianshang.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/members',type='http',auth="none",)
    def members(self,**post):
        template = env.get_template('members.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/questions',type='http',auth="none",)
    def questions(self,**post):
        template = env.get_template('questions.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/investment',type='http',auth="none",)
    def investment(self,**post):
        template = env.get_template('investment.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/deal',type='http',auth="none",)
    def deal(self,**post):
        template = env.get_template('deal.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/scanandpos',type='http',auth="none",)
    def scanandpos(self,**post):
        template = env.get_template('scanandpos.html')
        html = template.render(gituser=self._get_company())
        return html

    @http.route('/site/investment_register',type='http',auth="none",)
    def investment_register(self,**post):
        template = env.get_template('invest_register.html')
        html = template.render(gituser=self._get_company())
        return html


    @http.route('/site/invest_post', type='http', auth="none",methods=['POST'],csrf=False)
    def invest_post(self, **vals):
        parm = {
            'name': vals.get('name',False),
            'phone': vals.get('phone',False),
            'address': vals.get('address',False),
            'email': vals.get('email',False),
            'comment': vals.get('content',False),
            'is_investment': True,
        }
        request.registry['res.partner'].create(request.cr, SUPERUSER_ID, parm)

        #
        # #获取需要发送消息的用户
        # user_obj = request.registry['res.users']
        # users = user_obj.search(request.cr, SUPERUSER_ID,[('role_option','=',1)], context=request.context)
        #
        # if users:
        #     #发送通知给管理员
        #     message=u"有新招商客户,姓名：%s" % (vals.get('company_name',False))
        #     push_obj = request.registry['born.push']
        #
        #     for user in users:
        #         vals_message={
        #             'title':u'有新的公司注册',
        #             'phone':vals.get('phone',''),
        #             'content':message,
        #             'type':'boss',
        #             'state':'done',
        #             'user_id':user,
        #             'message_type':'1',
        #         }
        #         push_id = push_obj.create(request.cr, SUPERUSER_ID,vals_message,context=request.context)
        #         push_obj.send_message(request.cr, SUPERUSER_ID,push_id,context=request.context)

        return http.local_redirect('/site/invest_success',keep_hash=True)

    @http.route('/site/invest_success', type='http', auth="none",csrf=False)
    def invest_success_message(self):
        template = env.get_template('invest_success.html')

        html = template.render(title=u"注册成功")
        return html

    #增值服务
    @http.route('/site/server', type='http', auth="none",csrf=False)
    def server(self):
        template = env.get_template('server.html')
        html = template.render(gituser=self._get_company())
        return html


    @http.route('/site/test_weixin',type='http',auth="none",csrf=False)
    def test_weixin(self):
        template = env.get_template('test_weixin.html')
        html = template.render(gituser=self._get_company())
        return html