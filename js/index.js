const color_set = ['#ff7f7f', '#ff7fbf', '#ff7fff', '#bf7fff', '#7f7fff', '#7fbfff', '#7fffff', '#7fff7f', '#bfff7f', '#ffff7f', '#ffbf7f']


CodeActionListner();

$('#codeEditor').on('input', CodeActionListner);

function CodeActionListner() {
    let code = $('#codeEditor').val()
    let lineNum = code.match(/\n/g).length;
    let line_text = '', mark_text = '';
    for (let i = 0; i <= lineNum; i++) {
        line_text += `<div>${i + 1}</div>`;
        mark_text += `<div class="mark" id="${i + 1}">　</div>`
    }
    $('.line__number').html(line_text);
    $('.code__mark').html(mark_text);
}

$('#codeEditor').on('scroll', function () {
    let spos = $(this).scrollTop();
    $('.link').scrollTop(spos);
});

$('.mark').click(function(){
    $(this).css({ 'color': '#2f7dfa'});
    if($(this).text() == '　')
        $(this).text('■');
    else
        $(this).text('　');
})

$('#launch').click(function () {
    source = $('#codeEditor').val()
    console.log(source);
    $.ajax({
        url: '/csource',
        type: 'post',
        data: source,
        processData: false,
        contentType: false,
        cache: false,
    }).done(function (data) {
        line = Array();
        $(".mark").each(function(i, elem) {
            if($(elem).text() != '　')
                line.push($(elem).attr('id'))
        });
        console.log(line);
        $.ajax({
            url:'/breakpoint',
            type:'post',
            data:line,
            processData: false,
            contentType: false,
            cache: false,
        }).done(function(){
            $.get(`/launch`, function (data) {
            console.log(data)
            if (data.Output)
                output(data.Output)
            Initialize();
            for (let tidx in data.thread)
                AnalyzeThreadInfo(data.thread[tidx], data.pthread);
            InsertExtraTab();
            })
        }).fail(function(){
            alert("ブレイクポイントが設定できませんでした。");
        })
        
    }).fail(function () {
        // 失敗時の処理
        alert("コンパイルエラーが起きました。")
    });
});

$('#continue,#skip').click(function () {
    var com = $(this).attr('id')
    $.get(`/${com}`, function (data) {
        console.log(data)
        if (data.Output)
            output(data.Output)
        Initialize();
        if (data.state == 10) {
            alert('プログラムが終了しました。');
            $('textarea.output__text').text('');
            return;
        }
        for (let tidx in data.thread)
            AnalyzeThreadInfo(data.thread[tidx]);
        InsertExtraTab();
        //initFunc();
    })
})


$('button#input').click(function () {
    inputStr = $("#input").val()
    $.get('/input', {
        "inputStr": inputStr
    })
})


function output(out) {
    let outarea = $('textarea.output__text');
    let outtxt = outarea.text();
    outarea.text(outtxt + out);
    outarea.scrollTop(999);
}