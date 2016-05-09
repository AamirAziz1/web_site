function validate_email(emailvalue){
	var filter = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	if (!filter.test(emailvalue)) {
		return false;
	}else{
		return true;
	}
}


$(document).ready(function () {
	$('.register').each(function () {
		var register = this;
		
		//业务类型
	    $(register).on('change', "select[name='industry']", function () {
	    	var $select = $("select[name='industry']");
	        var city_obj = $.ajax({
	        	method: 'GET',
	        	url: "/site/json/get_industry_category",
	        	data: "industry_id="+$(this).val(),
	        	success: function(msg){
	        		var option_str = "<option value=''></option>";
	        		if(null != msg && msg.length>0){
	        			var obj = eval('(' + msg + ')');
	        			for (var prop in obj) { 
	    	        		option_str += "<option value=" + obj[prop].id + ">" + obj[prop].name + "</option>"
	    	        	}
	        		}
	        		$("select[name='industry_category']").empty();
	        		$("select[name='industry_category']").append(option_str);
	        	    return true;
	        	  }
	        });
	    }).change();
	    
	    $(register).on('change', "select[name='state_id']", function () {
	        var $select = $("select[name='area_id']");
	        var city_obj = $.ajax({
        	   type: "POST",
        	   url: "/site/json/get_city",
        	   data: "country_id="+$(this).val(),
        	   success: function(msg){
        			var option_str = "<option value=''></option>";		
        			if(null == msg || msg.length<=0){	        	    	
        			}else{
        				var obj = eval('(' + msg + ')');
        				for (var prop in obj) {  
        					option_str += "<option value=" + obj[prop].id + ">" + obj[prop].name + "</option>"
        				}
        			}	        
        	     $select.parent().show();
        	     $("select[name='area_id']").empty();
        	     $("select[name='subdivide_id']").empty();
        	     $("select[name='subdivide_id']").append("<option value=''></option>");
    	         $("select[name='area_id']").append(option_str); 
        	     return true;
        	   }
        	});
	    }).change();
	    
	    // 市
	    $(register).on('change', "select[name='area_id']", function () {
	        var $select = $("select[name='subdivide_id']");
	        var subdivide_obj = $.ajax({
	        	   type: "POST",
	        	   url: "/site/json/get_subdivide",
	        	   data: "states_id="+$(this).val(),
	        	   success: function(msg){
	        		 var option_str = "<option value=''></option>";		
	        	     if(null == msg || msg.length<=0){
	        	    	 
	        	     }else{
	        	    	var obj = eval('(' + msg + ')');
	    	        	for (var prop in obj) {  
	    	        		option_str += "<option value=" + obj[prop].id + ">" + obj[prop].name + "</option>"
	    	        	} 
	        	     }
	        	     $select.empty();
	        	     $select.append(option_str);
	        	     return true;
	        	   }
	        	});
	    }).change();
	});
});
