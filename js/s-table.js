const thead_key = ['address', 'mnemonic', 'operands'];
let markThreadTab = 1
let markFrameTab = 0

function Initialize() {
    $(".mark").each(function(i, elem) {
        if($(elem).text() != '■')
            $(elem).text('　');
        else
            $(elem).css({ 'color': '#2f7dfa'});
    });
    $('ul.thread__tab-button-ul').empty();
    $('ul.frame__tab-button-ul').empty();
    $('div.thread__table-area').empty();
}

function AnalyzeThreadInfo(thread, pthread) {
    let threadID = thread.IndexID;
    markAtCode(thread, threadID);
    let frame = thread.flist.filter(f => f.hasOwnProperty('line'))[0];
    InsertThreadTab(frame ? frame.name : `Thread${threadID}`, threadID);
    if (!frame)
        return;
    for(let frame of thread.flist){
        InsertFrameTab(frame);
        makeStable(frame);
    }

}

function markAtCode(thread, t_idx) {
    let frame = thread.flist.filter(f => f.hasOwnProperty('line'))[0];
    if (!frame)
        return;
    let line = frame.line;
    if ($(`#${line}.mark`).text() == '　'){
        $(`#${line}.mark`).css({ 'color': color_set[t_idx] });
        $(`#${line}.mark`).text('●');
    }else{
        $(`#${line}.mark`).css({ 'color': color_set[t_idx] });
    }

}

function makeStable(frame) {
    let stable = $('<table>').addClass('stable');
    let sthead =  $('<thead>').append('<tr>');

    for (idx in thead_key)
        sthead.find('tr').append($('<th>').text(thead_key[idx]));
    stable.append(sthead);
    let sbody = $('<tbody>');
    setSbody(frame, sbody);
    stable.append(sbody);

    let wrap = $('<div>').attr({ id: frame.ID });
    wrap.addClass('table__wrapper');
    if (markFrameTab != frame.ID)
        wrap.hide();
    $('div.thread__table-area').append(wrap.append(stable));
}

function setSbody(frame, sbody) {
    for(let stack of frame.slist){
        let tr = $('<tr>').addClass('str');
        for(let key in thead_key){
            var td = $('<td>').addClass('std');
            td.addClass(thead_key[key]);
            if (thead_key[key] == 'address')
                td.text(toHex(stack[thead_key[key]]));
            else
                td.text(stack[thead_key[key]]);
            tr.append(td);
        }
        sbody.append(tr);
    }
}

function InsertThreadTab(funcName, tid) {
    let tab_li = $('<li>').attr({
        class: 'thread__tab-button-li',
        id: tid
    });
    tab_li.text(funcName);
    tab_li.css({ 'background-color': color_set[tid] })
    tab_li.on('click', tabThreadFunc);
    if (markThreadTab == tid)
        tab_li.addClass("is-active");
    $(".thread__tab-button-ul").append(tab_li)

}
function InsertFrameTab(frame) {
    let tab_li = $('<li>').attr({
        class: 'frame__tab-button-li',
        id: frame.ID
    });
    tab_li.text(frame.name);
    //tab_li.css({ 'background-color': color_set[tid] })
    tab_li.on('click', tabFrameFunc);
    if (markFrameTab == frame.ID)
        tab_li.addClass("is-active");
    $(".frame__tab-button-ul").append(tab_li)

}
function toHex(v) {
    //console.log(typeof (v), v)
    if (typeof (v) != 'undefined')
        return '0x' + (('0000000000000000' + v.toString(16).toUpperCase()).substr(-16));
}

function varFunc(event) {
    let tr = $(event.target).parent();
    let selector = '';
    let trclass = tr.attr('class').split(' ');
    for (let idx in trclass) {
        selector += '.' + trclass[idx];
    }
    selector += '.' + tr.attr('id');
    selector = selectorEscape(selector);
    console.log(selector);
    console.log($(selector).css('display'));
    if ($(selector).css('display') == 'none')
        $(selector).show();
    else $(selector).hide();
}

function tabFrameFunc(event) {
    let tab = $(event.target);
    let other = $('ul.frame__tab-button-ul').children().not(tab);
    tab.addClass('is-active');
    other.removeClass('is-active');
    $('div.table__wrapper').hide();
    $(`div#${tab.attr('id')}.table__wrapper`).show();
    markFrameTab = tab.attr('id');
}

function tabThreadFunc(event){
    let tab = $(event.target);
    let other = $('ul.thread__tab-button-ul').children().not(tab);
    tab.addClass('is-active');
    other.removeClass('is-active');
    $('div.table__wrapper').hide();
    $(`div#${tab.attr('id')}.table__wrapper`).show();
    markThreadTab = tab.attr('id');
}

function set_wp(wplist, t_idx) {
    for (var wp_idx = 0; wp_idx < wplist.length; wp_idx++) {
        $(`tr#${wplist[wp_idx]}`).attr({ bgcolor: color_set[t_idx] })
    }
}

function selectorEscape(val) {
    return val.replace(/[ !"#$%&'()*+,\/:;<=>?@\[\\\]^`{|}~]/g, '\\$&');
}
