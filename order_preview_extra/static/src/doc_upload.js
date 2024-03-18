/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillStart } = owl;
import {ormService} from "@web/core/orm_service";

export class DocUpload extends Component {
    static template = "order_preview_extra.doc_upload";

    setup() {
        console.log('start');
        document.getElementsByClassName("card-body text-center")[0].style.display='none'
        this.state = useState({ type: "nat", files:[], ccname:'', ccnameback:'', servname:'', rutname:'', cycname:'', ccrname:'', ccrnameback:'', hidecc:false, hideccback: false, hideserv:false, hiderut:false, hidecyc:false, hideccr:false, hideccrback: false });

        /*this.orm = registry.category("services").content.orm;
        debugger;
        onWillStart(async () => {
            const order = this.orm.searchRead('sale.order',[],['name'])
            console.log(order)
        });*/
    }
    async uploadDoc() {
        console.log("upload file")


        if (this.state.type == "nat") {

            this.state.files.push({
                file: document.getElementById('ccFile'),
                type: 'cedula frente',
                sended: false
            })
               this.state.files.push({
                file: document.getElementById('ccFileBack'),
                type: 'cedula respaldo',
                sended: false
            })
            this.state.files.push({
                file: document.getElementById('servFile'),
                type: 'recibo servicio',
                sended: false
            })

        } else if (this.state.type == "emp") {
            this.state.files.push({
                file: document.getElementById('rutFile'),
                type: 'rut',
                sended: false
            })
            this.state.files.push({
                file: document.getElementById('camFile'),
                type: 'camara y comercio',
                sended: false
            })
            this.state.files.push({
                file: document.getElementById('ccrFile'),
                type: 'cedula representante frente',
                sended: false
            })
            this.state.files.push({
                file: document.getElementById('ccrFileBack'),
                type: 'cedula representante back',
                sended: false
            })
        }
        const archivoInput = document.getElementById('formFile');
        const orderId = document.getElementById('sale_order_id').innerText;
        for (const x of this.state.files) {
            const archivo = x.file.files[0];
            console.log(archivo)
            if (!archivo) {
                alert('Selecciona un archivo primero.');
                continue;
            }

            const formData = new FormData();
            formData.append('archivo', archivo);
            formData.append('orderId', parseInt(orderId));
            formData.append('type', x.type);
            await fetch('https://iptechservice.sivi.app/upload', {
                method: 'POST',
                body: formData,
            })
                .then(response => response.text())
                .then(data => {
                    x.sended = true
                    if(x.type=='cedula frente'){
                        this.state.hidecc = true
                        this.state.ccname = x.file.files[0].name
                    }
                    if(x.type=='cedula respaldo'){
                        this.state.hideccback = true
                        this.state.ccnameback = x.file.files[0].name
                    }
                    if(x.type=='recibo servicio'){
                        this.state.hideserv = true
                        this.state.servname = x.file.files[0].name
                    }
                    if(x.type=='rut'){
                        this.state.hiderut = true
                        this.state.rutname = x.file.files[0].name
                    }
                    if(x.type=='camara y comercio'){
                        this.state.hidecyc = true
                        this.state.cycname = x.file.files[0].name
                    }
                    if(x.type=='cedula representante'){
                        this.state.hideccr = true
                        this.state.ccrname = x.file.files[0].name
                    }
                    if(x.type=='cedula representante back'){
                        this.state.hideccrback = true
                        this.state.ccrnameback = x.file.files[0].name
                    }

                })
                .catch(error => {
                    console.error('Error al subir archivo:', error);
                });
        }

    }



}
