function setInputText(text, query_input_id){
    $(query_input_id).val(text);
    console.log('setInputText');
}

/*
function clickDropdownItem(text, suggest_area_id, query_input_id){
    $(suggest_area_id).empty();
    setInputText(text, query_input_id);
}
*/

function htmlEscape(rawText){
  if(typeof rawText !== 'string') {
    return rawText;
  }
  return rawText.replace(/[&'`"<>]/g, function(match) {
    return {
      '&': '&amp;',
      "'": '&#x27;',
      '`': '&#x60;',
      '"': '&quot;',
      '<': '&lt;',
      '>': '&gt;',
    }[match]
  });
}

function incremental_search(suggest_area_id, query_input_id){
    var input = $.trim($(query_input_id).val());
    $.ajax({
      url: '/search/product/ajax',
      type: 'GET',
      data: ('q=' + input),
      processData: false,
      contentType: false,
      dataType: 'json'
    })
    .done(function(data){
        $(suggest_area_id).empty()
        $(suggest_area_id).append('<div class="dropdown"><div class="dropdown-menu show" style="width:100%; margin-top:-10px"></div></div>');
      $(data).each(function(i, product){
        var dropdown_item = document.createElement('span');
        dropdown_item.innerHTML = htmlEscape(product.title).replace("&#x27;", "&quot;");
        dropdown_item.setAttribute('class', "dropdown-item");
        $(suggest_area_id+' > .dropdown > .dropdown-menu').append(dropdown_item);
        dropdown_item.addEventListener("click", function(){
            $(suggest_area_id).empty();
            setInputText(product.title, query_input_id);
        });
      });
    }).fail(function(){
        // エラーの場合処理
        $(suggest_area_id).empty()
    });
}

$(window).on('load', function(){
  $('#id_q').on('keyup', function(e){
    e.preventDefault();
    incremental_search('#main_suggest_area', '#id_q');
  });
});


$(window).on('load', function(){
  $('#header_query').on('keyup', function(e){
    e.preventDefault();
    incremental_search('#header_suggest_area', '#header_query');
  });
});


