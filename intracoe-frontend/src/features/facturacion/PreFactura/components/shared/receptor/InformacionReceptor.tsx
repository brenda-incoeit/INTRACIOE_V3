import { Receptor } from "../../../interfaces/facturaPdfInterfaces"

interface InformacionReceptorProps {
    receptor: Receptor
}

export const InformacionReceptor: React.FC<InformacionReceptorProps> = ({ receptor }) => {
    return (
        <>
            <h1 className="uppercase font-semibold pb-2">Receptor</h1>
            <div className="grid grid-cols-[auto_1fr] text-start gap-x-10 gap-y-10 border-2 border-border-color rounded-md px-5 py-3 ">
                <div className="flex flex-col gap-1 opacity-70">
                    <p>Nombre o razon social:</p>
                    <p>Documento identificacion:</p>
                    <p>Correo electronico:</p>
                    <p>telefono:</p>
                    <p>direccion:</p>
                </div>
                <div className="flex flex-col gap-1">
                    <p>{receptor.nombre}</p>
                    <p>{receptor.numDocumento} ({receptor.tipoDocumento})</p>
                    <p>{receptor.correo}</p>
                    <p>{receptor.telefono}</p>
                    <p>{receptor.direccion.complemento}</p>
                </div>
            </div>
        </>
    )
}