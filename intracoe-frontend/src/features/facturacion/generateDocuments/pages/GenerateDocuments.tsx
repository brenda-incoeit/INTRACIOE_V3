import { Divider } from 'primereact/divider';
import { WhiteSectionsPage } from '../../../../shared/containers/whiteSectionsPage';
import { Title } from '../../../../shared/text/title';
import { useEffect, useState } from 'react';
import { getAllEmpresas } from '../../../bussiness/configBussiness/services/empresaServices';
import { DatosEmisorCard } from '../components/Shared/datosEmisor/datosEmisorCard';
import { DropDownTipoDte } from '../components/Shared/configuracionFactura/tipoDocumento/DropdownTipoDte';
import { SelectCondicionOperacion } from '../components/Shared/configuracionFactura/condicionOperacion/selectCondicionOperacion';
import { SelectTipoTransmisión } from '../components/Shared/configuracionFactura/tipoTransmision/selectTipoTransmisión';
import { CheckBoxVentaTerceros } from '../components/Shared/configuracionFactura/ventaTerceros/checkboxVentaTerceros';
import { IdentifcacionSeccion } from '../components/Shared/identificacion.tsx/identifcacionSeccion';
import { SelectReceptor } from '../components/Shared/receptor/SelectReceptor';
import { TablaProductosAgregados } from '../components/FE/productosAgregados/tablaProductosAgregados';
import { ModalListaProdcutos } from '../components/FE/productosAgregados/modalListaProdcutos';
import { FormasdePagoForm } from '../components/Shared/configuracionFactura/formasDePago/formasdePagoForm';
import { ModalListaFacturas } from '../components/Shared/tablaFacturasSeleccionar/modalListaFacturas';
import { TablaProductosFacturaNotasCredito } from '../components/NotaCredito/tablaProductosFacturaNotasCredito';
import { TablaProductosFacturaNotasDebito } from '../components/NotaDebito/TablaProductosFacturaNotasDebito';
import { TablaProductosCreditoFiscal } from '../components/CreditoFiscal/TablaProductosCreditoFiscal';
import { ButtonDocumentosRelacionados } from '../components/Shared/configuracionFactura/documentosRelacionados/ButtonDocumentosRelacionados';
import { SelectModeloFactura } from '../components/Shared/configuracionFactura/modeloDeFacturacion/selectModeloFactura';
import { SendFormButton } from '../../../../shared/buttons/sendFormButton';

export const GenerateDocuments = () => {
  const [emisorData, setEmisorData] = useState({
    nit: '',
    nombre: '',
    telefono: '',
    email: '',
    direccion_comercial: '',
  });
  const [showProductsModal, setShowProductsModal] = useState(false);
  const [showfacturasModal, setShowfacturasModal] = useState(false);
  const [visibleDocumentoRelacionadomodal, setVisibleDocumentoRelacionadomodal] = useState(false);
  const [condicionDeOperacion, setCondicionDeOperacion] = useState("A contado")

  const [tipoDocumento, setTipoDocumento] = useState<{
    name: string;
    code: string;
  }>();

  useEffect(() => {
    fetchEmisarInfo();
  }, []);

  useEffect(() => {
    console.log('tipoDocumento', tipoDocumento);
  }, [tipoDocumento]);

  {/******** Consumo de API *******/ }
  const fetchEmisarInfo = async () => {
    try {
      const response = await getAllEmpresas();
      setEmisorData({
        nit: response[0].nit,
        nombre: response[0].nombre_razon_social,
        telefono: response[0].telefono,
        email: response[0].email,
        direccion_comercial: response[0].direccion_comercial,
      });
    } catch (error) {
      console.log(error);
    }
  };

  const generarFactura = () => {
    console.log('enviado');
  };

  {/*******************************/ }
  return (
    <>
      <Title text="Generar documentos" />

      {/* Seccion datos del emisor */}
      <WhiteSectionsPage>
        <>
          <div className="pt2 pb-5">
            <h1 className="text-start text-xl font-bold">Datos del emisor</h1>
            <Divider className="m-0 p-0"></Divider>
            <DatosEmisorCard
              nit={emisorData.nit}
              nombre={emisorData.nombre}
              telefono={emisorData.telefono}
              email={emisorData.email}
              direccion_comercial={emisorData.direccion_comercial}
            />
          </div>
        </>
      </WhiteSectionsPage>

      {/*Seccion configuración de factura*/}
      <WhiteSectionsPage>
        <>
          <div className="pt2 pb-5">
            <h1 className="text-start text-xl font-bold">
              Configuración factura
            </h1>
            <Divider className="m-0 p-0"></Divider>
            <div className="flex flex-col gap-8">
              <div className="flex flex-col items-start gap-1">
                <label className="opacity-70">Tipo de documento</label>
                <DropDownTipoDte
                  tipoDocumento={tipoDocumento}
                  setTipoDocumento={setTipoDocumento}
                />
              </div>
              <SelectCondicionOperacion condicionDeOperacion={condicionDeOperacion} setCondicionDeOperacion={setCondicionDeOperacion} />
              <SelectModeloFactura />
              <SelectTipoTransmisión />
              {tipoDocumento?.code != "04" && <FormasdePagoForm />}
              <CheckBoxVentaTerceros />
            </div>
          </div>
        </>
      </WhiteSectionsPage>

      {/*Seccion identificación*/}
      <WhiteSectionsPage>
        <div className="pt2 pb-5">
          <h1 className="text-start text-xl font-bold">Identificación</h1>
          <Divider className="m-0 p-0"></Divider>
          <IdentifcacionSeccion />
        </div>
      </WhiteSectionsPage>

      {/*Seccion receptor*/}
      <WhiteSectionsPage>
        <div className="pt2 pb-5">
          <h1 className="text-start text-xl font-bold">
            Seleccione el receptor
          </h1>
          <Divider className="m-0 p-0"></Divider>
          <SelectReceptor />
        </div>
      </WhiteSectionsPage>

      {/********* Seccion productos *********/}
      {/* Tipo de documento: FE */}
      {tipoDocumento?.code === "01" && (
        <WhiteSectionsPage>
          <div className="pt-2 pb-5">
            <div className="flex justify-between">
              <h1 className="text-start text-xl font-bold">
                Productos agregados
              </h1>
              <span className='flex gap-4'>
                <ButtonDocumentosRelacionados visible={visibleDocumentoRelacionadomodal} setVisible={setVisibleDocumentoRelacionadomodal} />
                <SendFormButton
                  className="bg-primary-blue rounded-md px-5 text-white hover:cursor-pointer text-nowrap"
                  onClick={() => setShowProductsModal(true)}
                  text={"Añadir producto"}
                />
              </span>
            </div>

            <Divider className=""></Divider>
            <TablaProductosAgregados />
            <ModalListaProdcutos
              visible={showProductsModal}
              setVisible={setShowProductsModal}
            />
          </div>
        </WhiteSectionsPage>
      )}

      {/* Tipo de documento: Nota de Creditos */}
      {tipoDocumento?.code === "04" && (
        <WhiteSectionsPage>
          <div className="pt-2 pb-5">
            <div className="flex justify-between">
              <h1 className="text-start text-xl font-bold">
                Factura seleccionada
              </h1>
              <button
                className="bg-primary-blue rounded-md px-5 py-3 text-white hover:cursor-pointer"
                onClick={() => setShowfacturasModal(true)}
              >
                seleccionar factura
              </button>
            </div>
            <Divider className="m-0 p-0"></Divider>
            <TablaProductosFacturaNotasCredito />
            <ModalListaFacturas
              visible={showfacturasModal}
              setVisible={setShowfacturasModal}
            />
          </div>
        </WhiteSectionsPage>
      )}

      {/* Tipo de documento: Nota de Debito */}
      {tipoDocumento?.code === "05" && (
        <WhiteSectionsPage>
          <div className="pt-2 pb-5">
            <div className="flex justify-between">
              <h1 className="text-start text-xl font-bold">
                Factura seleccionada
              </h1>
              <button
                className="bg-primary-blue rounded-md px-5 py-3 text-white hover:cursor-pointer"
                onClick={() => setShowfacturasModal(true)}
              >
                seleccionar factura
              </button>
            </div>
            <Divider className="m-0 p-0"></Divider>
            <TablaProductosFacturaNotasDebito />
            <ModalListaFacturas
              visible={showfacturasModal}
              setVisible={setShowfacturasModal}
            />
          </div>
        </WhiteSectionsPage>
      )}

      {/* Tipo de documento: Credito fiscal */}
      {tipoDocumento?.code === "02" && (
        <WhiteSectionsPage>
          <div className="pt-2 pb-5">
            <div className="flex justify-between">
              <h1 className="text-start text-xl font-bold">
                Factura seleccionada
              </h1>
              <button
                className="bg-primary-blue rounded-md px-5 py-3 text-white hover:cursor-pointer"
                onClick={() => setShowProductsModal(true)}
              >
                Seleccionar productos
              </button>
            </div>
            <Divider className="m-0 p-0"></Divider>
            <TablaProductosCreditoFiscal />
            <ModalListaProdcutos
              visible={showProductsModal}
              setVisible={setShowProductsModal}
            />
          </div>
        </WhiteSectionsPage>
      )}

      {/*Seccion totales resumen*/}
      <WhiteSectionsPage>
        <div className="pt-2 pb-5">
          <div className="flex justify-between">
            <h1 className="text-start text-xl font-bold">Resumen de totales</h1>
          </div>
          <Divider className="m-0 p-0"></Divider>
          <div className="grid grid-cols-4 gap-4 text-start">
            <p className="opacity-60">SubTotal Neto:</p>
            <p>$21.24</p>

            <p className="opacity-60">Total IVA:</p>
            <p>$2.78</p>

            <p className="opacity-60">Total con IVA:</p>
            <p>$21.24</p>

            <p className="opacity-60">Monto descuento:</p>
            <p>$0.0</p>

            <p>Total a pagar:</p>
            <p>$21.60</p>
          </div>
        </div>
      </WhiteSectionsPage>

      <div className="mx-14 flex">
        <button
          type="button"
          className="bg-primary-yellow mb-5 self-start rounded-md px-5 py-3 text-white hover:cursor-pointer"
          onClick={generarFactura}
        >
          Generar factura
        </button>
      </div>
    </>
  );
};
