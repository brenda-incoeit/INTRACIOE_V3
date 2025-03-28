import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import { generarFacturaService } from "../../services/facturavisualizacionServices";
import { InformacionEmisor } from "../../components/shared/header/InformacionEmisor";
import { CuerpoDocumento, CuerpoDocumentoDefault, DatosFactura, DatosFacturaDefault, Emisor, EmisorDefault, Extension, ExtensionDefault, Receptor, ReceptorDefault, Resumen, resumenTablaFEDefault } from "../../interfaces/facturaPdfInterfaces";
import { InformacionReceptor } from "../../components/shared/receptor/InformacionReceptor";
import { TablaVentaTerceros } from "../../components/shared/ventaTerceros/tablaVentaTerceros";
import { SeccionDocumentosRelacionados } from "../../components/shared/documentosRelacionados/seccionDocumentosRelacionados";
import { SeccionOtrosDocumentosRelacionados } from "../../components/shared/otrosDocumentosRelacionados/seccionOtrosDocumentosRelacionados";
import { TablaProductosFE } from "../../components/FE/tablaProductosFE";
import { TablaResumenFE } from "../../components/FE/tablaResumenFE";
import { PagoEnLetras } from "../../components/shared/extension/pagoEnLetras";
import { CondicionOperacion } from "../../components/shared/extension/CondicionDeOperacion";
import { SeccionExtension } from "../../components/shared/extension/seccionExtension";
import { Contactos } from "../../components/shared/footer/contactos";

import { Title } from "../../../../../shared/text/title";
import { FaFilePdf } from "react-icons/fa";
import { RiFileUploadFill } from "react-icons/ri";
import { FaCircleCheck } from "react-icons/fa6";
import { IoMdCloseCircle } from "react-icons/io";


import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { usePDF } from "react-to-pdf";
import { EnviarHacienda } from "../../../generateDocuments/services/factura/facturaServices";
import { Toast } from "primereact/toast";
import CustomToast, { CustomToastRef, ToastSeverity } from "../../../../../shared/toast/customToast";

const exportToPDF = async () => {
    const element = document.getElementById('content-id');
    if (!element) return;

    const canvas = await html2canvas(element, {
        useCORS: true,
        scale: 3, // mejor resolución
    });

    const imgData = canvas.toDataURL('image/png');

    const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'px',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();

    // 🧠 Calcular altura proporcional manteniendo aspecto
    const imgProps = {
        width: canvas.width,
        height: canvas.height,
    };

    const ratio = imgProps.height / imgProps.width;
    const imgHeight = pageWidth * ratio;
    const xOffset = (pageWidth - canvas.width * (pageWidth / canvas.width)) / 2;
    const imgWidth = pageWidth;

    // ✅ Añadir imagen con altura real proporcional
    pdf.addImage(imgData, 'PNG', xOffset, 0, imgWidth, imgHeight);
    pdf.save('factura.pdf');
};

export const FacturaVisualizacionPage = () => {
    let { id } = useParams();
    const [emisor, setEmisor] = useState<Emisor>(EmisorDefault)
    const [receptor, setReceptor] = useState<Receptor>(ReceptorDefault)
    const [datosFactura, setDatosFactura] = useState<DatosFactura>(DatosFacturaDefault)
    const [productos, setProductos] = useState<CuerpoDocumento[]>(CuerpoDocumentoDefault)
    const [resumen, setResumen] = useState<Resumen>(resumenTablaFEDefault)
    const [extension, setExtension] = useState<Extension>(ExtensionDefault)
    const [pagoEnLetras, setPagoEnLetras] = useState<string>("")
    const [condicionOperacion, setCondicionOperacion] = useState<number>(0)
    const navigate = useNavigate();
    const [visible, setVisible] = useState(false);
    const toastBC = useRef<Toast>(null);
    const { targetRef } = usePDF({ filename: 'page.pdf' });
    const toastRef = useRef<CustomToastRef>(null);

    const handleAccion = (severity: ToastSeverity, icon: any, summary: string) => {
        toastRef.current?.show({
            severity: severity,
            summary: summary,
            icon: icon,
            life: 2000
        });
    };

    const clear = () => {
        toastBC.current?.clear();
        setVisible(false);
    };

    useEffect(() => {
        fetchDatosFactura()
    }, [])

    const enviarHacienda = async () => {
        if (id) {
            try {
                const response = await EnviarHacienda(id);
                handleAccion('success', <FaCircleCheck size={32} />, 'La factura fue publicada correctamente');
                setInterval(() => navigate(0), 2000)
            } catch (error) {
                handleAccion('error', <IoMdCloseCircle size={38} />, 'Ha ocurrido un error al publicar la factura');
            }
        }
    };

    const fetchDatosFactura = async () => {
        try {
            if (id) {
                const response = await generarFacturaService(id)
                console.log(response.emisor)
                console.log(response.receptor)
                setEmisor(response.emisor)
                setDatosFactura(response.datosFactura)
                setReceptor(response.receptor)
                setProductos(response.productos)
                setResumen(response.resumen)
                setExtension(response.extension)
                setPagoEnLetras(response.pagoEnLetras)
                setCondicionOperacion(response.condicionOpeacion)
            }
        }
        catch (error) {
            console.log(error)
        }
    }

    return (
        <>
            <Title text="Factura generada con éxito" />

            <div className="flex justify-center gap-5">
                <button onClick={exportToPDF} className="bg-red-700 text-white rounded-md px-8 py-3 mb-7 mt-5">
                    <span className="flex gap-2 items-center justify-center">
                        <FaFilePdf size={24} />
                        <p>Descargar PDF</p>
                    </span>
                </button>
                {datosFactura.selloRemision == null && <button onClick={enviarHacienda} className="bg-primary-blue text-white rounded-md px-8 py-3 mb-7 mt-5">
                    <span className="flex gap-2 items-center justify-center">
                        <RiFileUploadFill size={24} />
                        <p>Publicar</p>
                    </span>
                </button>}
                <button onClick={() => navigate("/generar-documentos")} className="border border-primary-blue text-primary-blue bg-white rounded-md px-8 py-3 mb-7 mt-5">
                    Realizar otra factura
                </button>
            </div>
            <div id="content-id"
                style={{
                    fontSize: '1vw',
                    padding: '0.7vw 2vw',
                }}>
                <div className=" flex flex-col gap-5 py-8 px-10 my-2 bg-white" ref={targetRef}>
                    <InformacionEmisor emisor={emisor} datosFactura={datosFactura} />
                    <InformacionReceptor receptor={receptor} />
                    <TablaVentaTerceros />
                    <SeccionDocumentosRelacionados />
                    <SeccionOtrosDocumentosRelacionados />
                    <div className="flex flex-col">
                        <TablaProductosFE productos={productos} />
                        <div id='footer'>
                            <div className="grid grid-cols-2 pt-5 gap-x-5">
                                <span className="flex flex-col gap-3">
                                    <PagoEnLetras cantidadAPagar={pagoEnLetras} />
                                    <CondicionOperacion condicion={condicionOperacion} />
                                    <div className="border-2 border-border-color rounded-md text-start py-3 px-4">
                                        <div className="flex ">
                                            <p><span className="font-bold">Oberservaciones: </span>{extension.observaciones}</p>
                                            <p><span className="font-bold"></span>{extension.nombEntrega}</p>
                                        </div>
                                    </div>
                                    <SeccionExtension extension={extension} />
                                </span>
                                <span>
                                    <TablaResumenFE resumen={resumen} />
                                </span>
                            </div>
                            <Contactos emisor={emisor} />
                        </div>
                    </div>
                </div>
            </div>
            <CustomToast ref={toastRef} />
        </>
    )
}