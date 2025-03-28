import { useEffect } from "react"
import { CuerpoDocumento } from "../../interfaces/facturaPdfInterfaces"

interface TablaProductosFEInterface {
    productos: CuerpoDocumento[]
}

export const TablaProductosFE: React.FC<TablaProductosFEInterface> = ({ productos }) => {

    useEffect(() => {
        console.log("productos", productos)
        console.log(typeof (productos))

    }, [])
    return (
        <>
            <table className="table-auto border-2 w-full border-border-color text-start rounded-md ">
                <thead>
                    <tr className="text-center">
                        <th className="p-2 border-r-2 border-border-color text-center">N°</th>
                        <th className="p-2 border-r-2 border-border-color">Cantidad:</th>
                        <th className="p-2 border-r-2 border-border-color">Código</th>
                        <th className="py-2 pl-4 border-r-2 border-border-color text-start">Descripción</th>
                        <th className="p-2 border-r-2 border-border-color">Precio unitario</th>
                        <th className="p-2 border-r-2 border-border-color">Otros montos no afectos</th>
                        <th className="p-2 border-r-2 border-border-color">Descuento por item</th>
                        <th className="p-2 border-r-2 border-border-color">Ventas no sujetas</th>
                        <th className="p-2 border-r-2 border-border-color">Ventas exentas</th>
                        <th className="p-2">Ventas grabadas</th>
                    </tr>
                </thead>


                <tbody className="">
                    {
                        productos.map((producto, index) => (
                            <tr key={index}>
                                <td className="border-r-2 border-t-2 border-border-color text-center">{index + 1}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">{producto.cantidad}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">{producto.codigo}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4 text-start">{producto.descripcion}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">$ {producto.precioUni}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">$ 0</td> {/* TODO: */}
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">$ {producto.montoDescu}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">$ {producto.ventaNoSuj}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">$ {producto.ventaExenta}</td>
                                <td className="p-2 border-r-2 border-t-2 border-border-color pl-4">$ {producto.ventaGravada}</td>
                            </tr>
                        ))
                    }
                </tbody>
            </table>
        </>
    )
}