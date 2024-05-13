const showMenu=(toggleId,navId)=>{
    const toggle=document.getElementById(toggleId)
    let nav=document.getElementById(navId)

    toggle.addEventListener('click', () =>{
        nav.classList.toggle('show-menu')
        toggle.classList.toggle('show-icon')
    })
}

showMenu('nav-toggle','nav-menu')




