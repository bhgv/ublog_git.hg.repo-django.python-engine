$(document).ready(function()
{
  previous = 0 ;
  $('.toc ul ul ul').each(function()
  {
    $(this).prev('a').before('<span class="expander">+</span>')
    $(this).css('display', 'none')
  })
  $('.toc ul ul span').click(function(e)
  {
    $(this).html(
      $(this).next('a').next('ul').css('display') == 'none' ? '-' : '+'
    )
    $(this).next('a').next('ul').toggle() ;
  })
  /*$(window).scroll(function(e) {
    // not good: I want a smooth scroll so I need to detect if the scroll
    // position of the window let the top of the TOC visible or not
    if (previous < $(window).scrollTop())
    {
      if ($('.toc')[0].offsetHeight > window.innerHeight)
      {
        fixed = true
      }
      else
      {
        fixed = false ;
      }
    }
    else
    {
      fixed = false
    }
    if (!fixed && $(window).scrollTop()>135)
    {
      $('.toc').css('top', $(window).scrollTop()-100) ;
    }
    previous = $(window).scrollTop()
  })
  if (window.location.href.indexOf('#') != -1)
  {
    id = window.location.href.substr(window.location.href.indexOf('#'))
    window.scrollTo(id)
  }*/
})
