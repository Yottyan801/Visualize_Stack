const ahead_key = ['address', 'mnemonic', 'operands'];
const shead_key = ['address','contents'];
let tab_state = {'thread':1,'frame':0,'extra':0}
let return_ad_state ={}

function Initialize() {
    $(".mark").each(function(i, elem) {
        if($(elem).text() != '■')
            $(elem).text('　');
        else
            $(elem).css({ 'color': '#2f7dfa'});
    });
    $('ul.thread__tab-button-ul').empty();
    $('ul.frame__tab-button-ul').empty();
    $('ul.extra__tab-button-ul').empty();
    $('div.thread__table-area').empty();
}

function AnalyzeThreadInfo(thread, pthread) {
    let threadID = thread.IndexID;
    markAtCode(thread, threadID);
    InsertThreadTab(`Thread${threadID}`, threadID);
    for(let fname in thread.flist){
        frame = thread.flist[fname]
        if(!return_ad_state.hasOwnProperty(frame.name)){
            return_ad_state[frame.name] = frame.return_ad
        }else{
            if(return_ad_state[frame.name] != frame.return_ad)
                alert(`${frame.name} no retrun address ga kawarimasita`);
        }
        InsertFrameTab(frame,threadID);
        makeStable(frame,threadID);
        makeAtable(frame,threadID);
        
    }
    $('div.table__wrapper').hide();
    $(`div.table__wrapper.thread${tab_state.thread}.frame${tab_state.frame}.extra${tab_state.extra}`).show();
}

function markAtCode(thread, t_idx) {
    let line = -1;
    for(let frame in thread.flist){
        if(thread.flist[frame].hasOwnProperty('line'))
            line = thread.flist[frame].line
    }
    console.log(line)
    if(!line)return;
    if ($(`#${line}.mark`).text() == '　'){
        $(`#${line}.mark`).css({ 'color': color_set[t_idx] });
        $(`#${line}.mark`).text('●');
    }else{
        $(`#${line}.mark`).css({ 'color': color_set[t_idx] });
    }
}
function makeStable(frame,threadID) {
    let stable = $('<table>').addClass('stable');
    let sthead =  $('<thead>').append('<tr>');

    for (idx in shead_key)
        sthead.find('tr').append($('<th>').text(shead_key[idx]));
    stable.append(sthead);
    let sbody = $('<tbody>');
    setSbody(frame, sbody);
    stable.append(sbody);

    let wrap = $('<div>').addClass(`thread${threadID} frame${frame.ID} extra0`);
    wrap.addClass('table__wrapper');
    wrap.addClass(`threadID${threadID}`);
    let CFA = $('<div>').text(`CFA:${frame.CFA}`);
    let PC = $('<div>').text(`PC:${frame.PC}`);
    let SP = $('<div>').text(`SP:${frame.SP}`);
    let FP = $('<div>').text(`FP:${frame.FP}`);
    let return_ad = $('<div>').text(`return_address:${frame.return_ad}`);
    wrap.append(CFA);
    wrap.append(PC);
    wrap.append(SP);
    wrap.append(FP);
    wrap.append(return_ad);
    
    if (tab_state.frame!= frame.ID)
        wrap.hide();
    $('div.thread__table-area').append(wrap.append(stable));
}

function makeAtable(frame,threadID) {
    let stable = $('<table>').addClass('stable');
    let sthead =  $('<thead>').append('<tr>');

    for (idx in ahead_key)
        sthead.find('tr').append($('<th>').text(ahead_key[idx]));
    stable.append(sthead);
    let sbody = $('<tbody>');
    setAbody(frame, sbody);
    stable.append(sbody);

    let wrap = $('<div>').addClass(`thread${threadID} frame${frame.ID} extra1`);
    wrap.addClass('table__wrapper');
    wrap.addClass(`threadID${threadID}`);
    let CFA = $('<div>').text(`CFA:${frame.CFA}`);
    let PC = $('<div>').text(`PC:${frame.PC}`);
    let SP = $('<div>').text(`SP:${frame.SP}`);
    let FP = $('<div>').text(`FP:${frame.FP}`);
    let return_ad = $('<div>').text(`return_address:${frame.return_ad}`);
    wrap.append(CFA);
    wrap.append(PC);
    wrap.append(SP);
    wrap.append(FP);
    wrap.append(return_ad);
    
    if (tab_state.frame != frame.ID)
        wrap.hide();
    $('div.thread__table-area').append(wrap.append(stable));
}

function setAbody(frame, sbody) {
    for(let addr in frame.alist){
        let tr = $('<tr>').addClass('atr');
        for(let key in ahead_key){
            var td = $('<td>').addClass('atd');
            td.addClass(ahead_key[key]);
            if (ahead_key[key] == 'address'){
                console.log(return_ad_state)
                for(fname in return_ad_state){
                    return_ad = parseInt(Number(return_ad_state[fname]),10)
                    if(return_ad == parseInt(Number(addr),10))
                        tr.addClass('return_ad');
                }
                td.text(toHex(addr));
            }
            else
                td.text(frame.alist[addr][ahead_key[key]]);
            tr.append(td);
        }
        sbody.append(tr);
    }
}
function setSbody(frame, sbody) {
    for(let stack in frame.slist){
        let tr = $('<tr>').addClass('str');
        for(let key in shead_key){
            var td = $('<td>').addClass('std');
            td.addClass(shead_key[key]);
            if (shead_key[key] == 'address'){
                td.text(toHex(stack));
            }else if(isObject(frame.slist[stack])){
                vdict = frame.slist[stack]
                for(key in vdict){
                    if(key == 'attr')
                        continue;
                    ptag = $('<p>').text(`${key}:${vdict[key]}`)
                    td.append(ptag);
                }
            }else{
                fp_ad = parseInt(Number(frame.FP),10)
                if(fp_ad+8 == parseInt(Number(stack),10))
                    td.addClass('return_ad');
                td.text(frame.slist[stack]);
            }
            tr.append(td);
        }
        sbody.append(tr);
    }
}

function InsertThreadTab(funcName, tid) {
    let tab_li = $('<li>').attr({
        class: 'thread__tab-button-li',
        id: tid,
        type:'thread'
    });
    tab_li.text(funcName);
    tab_li.css({ 'background-color': color_set[tid] })
    tab_li.on('click', tabFunc);
    if (tab_state.thread == tid)
        tab_li.addClass("is-active");
    $(".thread__tab-button-ul").append(tab_li)

}
function InsertFrameTab(frame, threadID) {
    let tab_li = $('<li>').attr({
        class: 'frame__tab-button-li',
        id: frame.ID,
        type:'frame'
    });
    tab_li.text(frame.name);
    tab_li.addClass(`thread${threadID}`);
    //tab_li.css({ 'background-color': color_set[tid] })
    tab_li.on('click', tabFunc);
    if (tab_state.frame== frame.ID)
        tab_li.addClass("is-active");
    $(".frame__tab-button-ul").append(tab_li)
    $('li.frame__tab-button-li').hide();
    $(`li.thread${tab_state.thread}`).show();

}
function InsertExtraTab(){

    let tab_Assembly = $('<li>').attr({
        class: 'extra__tab-button-li',
        id:1,
        type:'extra'
    });
    let tab_Stack    = $('<li>').attr({
        class: 'extra__tab-button-li',
        id:0,
        type:'extra'
    });
    tab_Assembly.text('Assembly');
    tab_Stack.text('Stack');
    tab_Assembly.on('click', tabFunc);
    tab_Stack.on('click', tabFunc);

    if (tab_state.extra == 0)
        tab_Assembly.addClass("is-active");
        $(".extra__tab-button-ul").append(tab_Stack);
    $(".extra__tab-button-ul").append(tab_Assembly);
    
}
function toHex(v) {
    //console.log(typeof (v), v)
    if (typeof (v) != 'undefined')
        return '0x' + (('0000000000000000' + v.split('0x')[1].toString(16).toUpperCase()).substr(-16));
}

function tabFunc(event) {
    let tab = $(event.target);
    let type = tab.attr('type');
    let other = $(`ul.${type}__tab-button-ul`).children().not(tab);
    tab_state[type] = tab.attr('id');
    tab.addClass('is-active');
    other.removeClass('is-active');
    if(type == 'thread'){
        $('li.frame__tab-button-li').hide();
        $(`li.thread${tab_state.thread}`).show();
    }
    $('div.table__wrapper').hide();
    $(`div.table__wrapper.thread${tab_state.thread}.frame${tab_state.frame}.extra${tab_state.extra}`).show();
}

function set_wp(wplist, t_idx) {
    for (var wp_idx = 0; wp_idx < wplist.length; wp_idx++) {
        $(`tr#${wplist[wp_idx]}`).attr({ bgcolor: color_set[t_idx] })
    }
}

function selectorEscape(val) {
    return val.replace(/[ !"#$%&'()*+,\/:;<=>?@\[\\\]^`{|}~]/g, '\\$&');
}

function isObject(value) {
    return value !== null && typeof value === 'object'
  }