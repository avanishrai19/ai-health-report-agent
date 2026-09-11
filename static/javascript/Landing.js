const text="Welcome to AI Health Report Analyzer";

let i=0;

function typeWriter(){

if(i<text.length){

document.getElementById("typewriter").innerHTML+=text.charAt(i);

i++;

setTimeout(typeWriter,60);

}

}

window.onload=typeWriter;