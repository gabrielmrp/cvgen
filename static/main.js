document.addEventListener('DOMContentLoaded', function() {
        function findParentWithClass(element, className) {
        while (element && !element.classList.contains(className)) {
            element = element.parentElement;
        }
            return element;
        }


    function createModal(element) {
        let modal = document.createElement('div');
        modal.className = 'modal';

        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';

        const closeBtn = document.createElement('span');
        closeBtn.className = 'close'; 
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function() {
            modal.style.display = 'none';
        };

        const title = document.createElement('h2')
        title.classList.add('modal_div')
        title.innerText = 'Localização do conteúdo:'; 

        const modalText1 = document.createElement('span');
        modalText1.className = 'modalText1';
        modalText1.classList.add('mb-2');
        modalText1.innerHTML = element.getAttribute('title');

        const hr = document.createElement('hr');
        const modalText2 = document.createElement('span');
        modalText2.className = 'modalText2';
        modalText2.classList.add('mb-2');
        modalText2.innerHTML = 'Outro conteúdo relevante aqui.';

        modalContent.appendChild(closeBtn);
        modalContent.appendChild(title);   
        modalContent.appendChild(modalText1); 
        modalContent.appendChild(hr);
        modalContent.appendChild(modalText2);
        modal.appendChild(modalContent);



        findParentWithClass(element, 'alias') .appendChild(modal, element.nextSibling);
        return modal;
    }

    function initializeModal(element) {
        const modal = createModal(element);

        const modelo = 'modelos/' + document.getElementById('modelo').innerText+'.txt';
        const planilha = document.getElementById('planilha').innerText;
        const modalText1 = modal.querySelector('.modalText1');
        const modalText2 = modal.querySelector('.modalText2');

        let isHovered = false;
        let ctrlPressed = false;

        element.addEventListener('mouseenter', function() {
            //console.log(element);
            isHovered = true;
            checkDisplay();
        });

        element.addEventListener('mouseleave', function() {
            isHovered = false;
            //checkDisplay();
        });

        document.addEventListener('keydown', function(event) {
            if (event.key === 'Control') {
                ctrlPressed = true;
                checkDisplay();
            }
        });

        document.addEventListener('keyup', function(event) {
            if (event.key === 'Control') {
                ctrlPressed = false;
                checkDisplay();
            }
        });



     

        function checkDisplay() {
            if (isHovered && ctrlPressed) {

                if(element.classList.contains('section_title')){
                    const title = element.getAttribute('title') ;
                     parts = title.split(' | ')
                     modalText1.innerHTML = parts[0].replace('modelo.txt',modelo);
                     modalText2.innerHTML = parts[1].replace('nome : novonome',element.getAttribute('id')+' : novonome');
                     modal.style.display = 'block';
                }
                else{

                    const title = element.getAttribute('title') ;
                    const idioma = document.getElementById('idioma').innerText ;

                    const places = title.split(';');
                    let parts = places[0].split(':');
                    parts[1] = parts[1].replace("alias",findParentWithClass(element, 'alias').getAttribute('title'))

                    let pos = parts[1].split('/'); 

                    console.log(pos)


                    alias_ou_grupo='alias'
                    if(pos[1]=='grupo')
                    {
                        alias_ou_grupo='grupo'
                        pos[1] = places[1].split(':')[1].split('/')[2].slice(5)
                    }


                    if(pos[2]!='alias')
                    {
                        pos[2] = pos[2] + '_' + idioma
                    }


                    texto1 = ''
                     

                    if(pos[2].slice(0,5)=='grupo'){
                         texto1 += 's'
                     }

                     texto1 += `Na ${parts[0]} <b>${planilha}</b>, acesse a aba <b>${pos[0]}</b>
                     encontre a linha cujo valor de ${alias_ou_grupo} seja <b>${pos[1]}</b> e então acesse a coluna <b>${pos[2]}</b>.`;
                    
                    

                    parts = places[1].split(':');
                    pos = parts[1].split('/');

                    let texto2 = ''
                    
                    //console.log(pos)
                    if (pos.length > 2) { 
                        if(pos[2].slice(0,5)=='grupo'){
                            
                            texto2 += "e verifique que o grupo que contem a habilidade é : <b>"+pos[2].slice(5)+"</b>.<br />"
                             
                        }
                        else{ 


                         if(places[0].split(':')[1].split('/')[2].slice(0,7)==='detalhe'){
                             texto2 +=`No ${parts[0]} <b>${modelo}</b>, localize a sequência <b>${pos[0]}</b> -> <b>${pos[1]}</b> `;
                             texto2 += `-> <b>${pos[2].replace("alias",findParentWithClass(element, 'alias').getAttribute('title'))}</b>.<br />`
                             texto2 += 'Os detalhes são habilitados pelo símbolo "...", os remova para suprimí-los' 
                        }
                        else{
                             texto2 +=`No ${parts[0]} <b>${modelo}</b>, localize a sequência <b>${pos[0]}</b> -> <b>${pos[1]}</b> `;
                             texto2 += `-> <b>${pos[2].replace("alias",findParentWithClass(element, 'alias').getAttribute('title'))}</b>.<br />`
                             texto2 += "Para remover o item basta retirar esse grupo no lugar apontado acima"
                        }
                      }
                     }
                    
                        

                    
                   
                    texto2 += '.' 

                    modalText1.innerHTML = texto1;
                    modalText2.innerHTML = texto2;
                    modal.style.display = 'block';

                }
                 
                
            } else {
                modal.style.display = 'none';
            }
        }
    }

    const elements = document.querySelectorAll('.detalhes');
    elements.forEach(function(element) {
        initializeModal(element);
    });
});
