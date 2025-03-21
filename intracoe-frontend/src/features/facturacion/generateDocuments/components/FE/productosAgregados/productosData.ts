export const productosData = [
  {
    id: 1,
    codigo: '001',
    descripcion: 'PCH405 - leche entera ira 26 250gb',
    precio_unitario: '10.00',
    cantidad: 2,
    descuento: 0,
    no_grabado: false,
    iva_unitario: 0,
    total_neto: 0,
    total_con_iva: 0,
    total_iva: 0,
    seleccionar: false,
    monto_a_anular: 0,
    iva_percibido: 0,
  },
  {
    id: 2,
    codigo: '002',
    descripcion: 'PCH405 - leche entera ira 26 250gbsssss',
    precio_unitario: '20.00',
    cantidad: 3,
    descuento: 0,
    no_grabado: false,
    iva_unitario: 0,
    total_neto: 0,
    total_con_iva: 0,
    total_iva: 0,
    seleccionar: false,
    monto_a_anular: 0,
    iva_percibido: 0,
  },
];

export interface Product {
  id: number;
  codigo: string;
  descripcion: string;
  precio_unitario: string;
  cantidad: number;
  no_grabado: boolean;
  descuento: number;
  iva_unitario: number;
  total_neto: number;
  total_iva: number;
  total_con_iva: number;
  iva_percibido: number;
  seleccionar: boolean;
}
