$(document).ready(function(){
    var arrLang = {
        'en' : {
            'tof camera login' : 'TOF CAMERA LOGIN',
            'login' : 'Login',
            'footer' : 'Copyright (C) 2019 BRYCEN Co., Ltd.',
            'depth imaging solution' : 'DEPTH IMAGING SOLUTION',
            'BRYCEN Co., Ltd.' : 'BRYCEN Co., Ltd.',
            'username' : 'Username',
            'password' : 'Password',
            'login fail':'The user name or password is incorrect.',
            'camera panel' : 'CAMERA PANEL',
            'control panel' : 'CONTROL PANEL',
            'range' : 'Range',
            'mode' : 'Mode',
            'light source' : 'Light source',
            'ir gain' : 'IR Gain',
            'pulse count' : 'Pulse Count',
            'coring threshold' : 'Coring Threshold',
            'In-camera noise reduction filter' : '  In-camera noise reduction filter',
            'status' : 'Status',
            'apply' : 'APPLY',
            'welcome' : 'Welcome',
            'log out' : 'log out',
            'zoom' : 'Zoom',
            'operating' : 'operating',	
            'Brightness' : 'Adjust brightness',
            'Default' : 'Reset',
            'Reset' : 'Reset',
            'Name file' : 'Filename',
            'Save the current parameter values' : 'Save the current parameter values',
            'Params profile' : 'Params profile',
            'Save as profile' : 'Save as profile',
            'err_record' : 'Stop recording because login error',
            'sys_working' : 'The system is busy. Try again later!',
            'Zoom' : 'Zoom (%)',
            'Return display main' : 'Return display main',
            'DEPTH IMAGE' : 'DEPTH IMAGE',
            'IR IMAGE' : 'IR IMAGE'
        },
        'jp' : {
            'tof camera login' : 'TOFカメラログイン',
            'login' : 'ログイン',
            'footer' : '著作権 (C) 2019 BRYCEN Co., Ltd.',
            'depth imaging solution' : '距離画像ソリューション',
            'BRYCEN Co., Ltd.' : '株式会社ブライセン',
            'username' : 'ユーザー名',
            'password' : 'パスワード',
            'login fail':'ユーザー名またはパスワードが正しくありません.',
            'camera panel' : 'カメラパネル',
            'control panel' : 'コントロールパネル',
            'range' : '範囲',
            'mode' : 'モード',
            'light source' : '光源',
            'ir gain' : 'IR ゲイン',
            'pulse count' : 'パルスカウント',
            'coring threshold' : 'コアリング閾値',
            'In-camera noise reduction filter' : '  カメラ内ノイズ低減フィルター',
            'status' : '状態',
            'apply' : '適用',
            'welcome' : 'ようこそ',
            'log out' : 'ログアウト',
            'zoom' : 'ズーム',
            'operating' : '作動中',
            'Brightness' : '明るさ',
            'Default' : '既定',
            'Reset' : '既定',
            'Name file' : 'ファイル名',
            'Save the current parameter values' : '現在のパラメーター値を保存する',
            'Params profile':'パラメータファイル',
            'Save as profile' : 'ファイルとして保存',
            'err_record' : 'ログインエラーのため記録を停止',
            'sys_working' : 'システムはビジーです。 リトライ',
            'Zoom' : 'ズーム (%)',
            'Return display main' : 'メイン画面に戻る',
            'DEPTH IMAGE' : '深度画像',
            'IR IMAGE' : 'IR 画像'
        },
        'vn' : {
            'tof camera login' : 'ĐĂNG NHẬP MÁY ẢNH TOF',
            'login' : 'ĐĂNG NHẬP',
            'footer' : 'Bản quyền (C) 2019 BRYCEN Co., Ltd.',
            'depth imaging solution' : 'GIẢI PHÁP HÌNH ẢNH CHIỀU SÂU',
            'BRYCEN Co., Ltd.' : 'BRYCEN Co., Ltd.',
            'username' : 'Tên người dùng',
            'password' : 'Mật khẩu',
            'login fail':'Tên người dùng hoặc mật khẩu không chính xác',
            'camera panel' : 'MÁY ẢNH',
            'control panel' : 'BẢNG ĐIỀU KHIỂN',
            'range' : 'Phạm vi',
            'mode' : 'Chế độ',
            'light source' : 'Nguồn sáng',
            'ir gain' : 'IR Gain',
            'pulse count' : 'Pulse Count',
            'coring threshold' : 'Coring Threshold',
            'In-camera noise reduction filter' : 'Dùng bộ lọc nhiễu máy ảnh',
            'status' : 'Trạng thái',
            'apply' : 'GỬI',
            'welcome' : 'Chào mừng',
            'log out' : 'Đăng xuất',
            'zoom' : 'Zoom',
            'operating' : 'Đang hoạt động',	
            'Brightness' : 'Chỉnh sáng',
            'Default' : 'Mặc định',
            'Reset' : 'Mặc định',
            'Name file' : 'Filename',
            'Save the current parameter values' : 'Save the current parameter values',
            'Params profile' : 'Thông số mẫu',
            'Save as profile' : 'Save as profile',
            'err_record' : 'Dừng ghi video vì lỗi đăng nhập',
            'sys_working' : 'Hệ thống đang bận. Thử lại sau !',
            'Zoom' : 'Thu/Phóng (%)',
            'Return display main' : 'Quay lại giao diện chính',
            'DEPTH IMAGE' : 'DEPTH IMAGE',
            'IR IMAGE' : 'IR IMAGE'
        }
    };
    $(function(){
        $("div[title|='translate']").click(function(){
        var lang = $(this).attr('id');
        $("div[title|=''],div[title|=''],h4[title|=''],h3[title|=''],span[title|=''],span[title|=''],span[title|=''],span[title|='']").each(function(index,element){
            $(this).text(arrLang[lang][$(this).attr('key')]);         
        });
        $(".submit,#submit").each(function(index,element){
            $(this).val(arrLang[lang][$(this).attr('key')]);         
        });     
        $("input[title|=''],input[title|='']").each(function(index,element){
            $(this).attr('placeholder', arrLang[lang][$(this).attr('key')] );         
        });  
        $("#default_option,.title").each(function(index,element){
            $(this).attr('value', arrLang[lang][$(this).attr('key')] );         
        });       
        if($('.mes').text() == ' '){
            $(".mes").each(function(index,element){
            $(this).text(arrLang[lang][$(this).attr('key')]);            
            });  
        }  
        if($('.temperature_number').val() == "operating"){
            $("input[title|='operating']").each(function(index,element){
            $(this).val(arrLang[lang][$(this).attr('key')]);         
            });
        }      
        });       
    });

    $(function(){
        var lang = $('.language').val();
        var btn_jp = document.getElementById('jp')
        var btn_en = document.getElementById('en')
        var btn_vn = document.getElementById('vn')
        if(lang == "en"){
            setTimeout(function(){
                btn_en.click()
            })
        }else if(lang == "jp"){
            setTimeout(function(){
                btn_jp.click();
                $('.label_profile').css('width','145px');
                $('#default_option').css('width','90px');
                $('#insert').css('right','1');
            })
        }else if(lang == "vn"){
            setTimeout(function(){
                btn_vn.click()    
            })
        }else if(lang == ""){
            setTimeout(function(){
                btn_jp.click()         
            })
        }
        
    });
})