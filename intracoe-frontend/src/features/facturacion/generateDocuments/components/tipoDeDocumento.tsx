import { Divider } from "antd"
import { WhiteSectionsPage } from "../../../../shared/containers/whiteSectionsPage"

interface TipoDeDocumentoInterface{
    nit: string,
    nombre: string,
    telefono: string,
    email: string,
    direccion_comercial: string
}

export const TipoDeDocumento:React.FC<TipoDeDocumentoInterface> = ({nit, nombre, telefono, email, direccion_comercial}) => {
    return (
        <WhiteSectionsPage>
            <div className='pt2 pb-5'>
                <h1 className="text-start font-bold text-xl">Datos del emisor</h1>
                <Divider className="m-0 p-0"></Divider>
                <div className='grid grid-cols-[20%_80%] justify-start items-start gap-4 font-medium'>
                    <span className="text-start text-black opacity-50">NIT:</span>
                    <span className='text-start'>{nit}</span>
                    <span className="text-start text-black opacity-50">Nombre:</span>
                    <span className='text-start'>{nombre}</span>
                    <span className="text-start text-black opacity-50">Teléfono:</span>
                    <span className='text-start'>{telefono}</span>
                    <span className="text-start text-black opacity-50">Correo:</span>
                    <span className='text-start'>{email}</span>
                    <span className="text-start text-black opacity-50">Dirección comercial:</span>
                    <span className='text-start'>{direccion_comercial}</span>
                </div>
            </div>
        </WhiteSectionsPage>
    )
}
