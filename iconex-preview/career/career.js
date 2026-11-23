/* iCONEX Career — career-only interactions; no external data collection endpoint. */
(function(){
'use strict';
const menu=document.getElementById('menu'),drawer=document.getElementById('iconex-nav-drawer'),close=drawer?.querySelector('.ix-close');
let trigger=null;
function shut(){if(!drawer?.open)return;drawer.close();document.body.style.overflow='';menu?.setAttribute('aria-expanded','false');trigger?.focus();}
menu?.addEventListener('click',()=>{trigger=document.activeElement;drawer.showModal();document.body.style.overflow='hidden';menu.setAttribute('aria-expanded','true');close?.focus()});
close?.addEventListener('click',shut);
drawer?.addEventListener('cancel',e=>{e.preventDefault();shut()});
drawer?.addEventListener('click',e=>{if(e.target===drawer)shut()});
const eventButton=document.getElementById('ix-events-toggle'),eventLinks=document.getElementById('ix-events-links');
eventButton?.addEventListener('click',()=>{const open=eventLinks.hidden;eventLinks.hidden=!open;eventButton.setAttribute('aria-expanded',String(open))});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&eventLinks&&!eventLinks.hidden){eventLinks.hidden=true;eventButton.setAttribute('aria-expanded','false');eventButton.focus()}});
const select=document.getElementById('career-interest'),form=document.getElementById('career-application'),status=document.getElementById('career-status');
document.querySelectorAll('[data-career-interest]').forEach(button=>button.addEventListener('click',()=>{select.value=button.dataset.careerInterest;select.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});select.focus({preventScroll:true})}));
form?.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;const data=new FormData(form);const fields=[['Name',data.get('name')],['Email',data.get('email')],['Area of interest',data.get('interest')],['Portfolio / LinkedIn',data.get('portfolio')||'Not provided'],['Event experience',data.get('experience')||'Not provided']];const subject='iCONEX Career Interest — '+String(data.get('interest'));const body=fields.map(([label,value])=>label+': '+value).join('\n\n');const url='mailto:connect@iconex.in?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);status.textContent='Your email application is prepared. Please send it from your email app to complete your enquiry. No details have been submitted to this website.';window.location.href=url;});
const footerHost=document.getElementById('career-shared-footer');if(footerHost&&typeof window.iconexConversionFooter==='function')footerHost.innerHTML=window.iconexConversionFooter();
})();
