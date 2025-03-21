export interface ActivitiesData {
  id: number;
  codigo: string;
  descripcion: string;
}

export interface ActivitiesDataNew {
  codigo: string;
  descripcion: string;
}

export const defaultEmisorData: EmisorInterface = {
  nit: '',
  nrc: '',
  nombre_razon_social: '',
  nombre_comercial: '',
  direccion_comercial: '',
  telefono: '',
  email: '',
  codigo_punto_venta: '', //codigo
  codigo_establecimiento: '',
  nombre_establecimiento: null,
  tipoestablecimiento: {
    id: "",
    descripcion: "",
    code: "",
  },
  departamento: {
    id: "",
    descripcion: "",
    code: "",
  },
  municipio: {
    id: "",
    descripcion: "",
    code: "",
  },
  ambiente: {
    id: "",
    descripcion: "",
    code: "",
  },
  tipo_documento: {
    id: "",
    descripcion: "",
    code: "",
  },
  actividades_economicas: [],
  tipo_establecimiento_codigo: ""
};


export interface EmisorInterface {
  nit: string;
  nrc: string;
  nombre_razon_social: string;
  nombre_comercial: string;
  direccion_comercial: string;
  telefono: string;
  email: string;
  codigo_establecimiento: string;
  codigo_punto_venta: string;
  nombre_establecimiento: string | null;
  tipoestablecimiento: TipoEstablecimiento;
  tipo_establecimiento_codigo: string
  departamento: Departamento;
  municipio: Municipio;
  ambiente: Ambiente;
  tipo_documento: TipoDocumento;
  actividades_economicas: ActivitiesData[]; // Array de IDs de actividades económicas
}

export const defaulReceptorData: ReceptorInterface = {
  tipo_documento: { id: '', descripcion: '', code: '' },
  num_documento: '',
  nrc: '',
  nombre_establecimiento: '',
  nombre_comercial: '',
  actividades_economicas: [],
  departamento: { id: '', descripcion: '', code: '' },
  municipio: { id: '', descripcion: '', code: '' },
  direccion: '',
  telefono: '',
  correo: '',
}
export interface ReceptorInterface {
  tipo_documento: TipoDocumento,
  num_documento: string,
  nrc: string,
  nombre_establecimiento: string,
  actividades_economicas: ActivitiesData[]
  municipio: { id: string, descripcion: string, code: string },
  departamento: { id: string, descripcion: string, code: string },
  direccion: string,
  telefono: string,
  correo: string,
  nombre_comercial: string
}

export interface TipoDocumento {
  id: string;
  descripcion: string;
  code: string;
}

export interface Ambiente {
  id: string;
  descripcion: string;
  code: string;
}
export interface TipoEstablecimiento {
  id: string;
  descripcion: string;
  code: string;
}
export interface Departamento {
  id: string;
  descripcion: string;
  code: string;
}

export interface Municipio {
  id: string;
  descripcion: string;
  code: string;
}

export interface RequestEmpresa {
  nit: string;
  nrc: string;
  nombre_razon_social: string;
  nombre_comercial: string;
  direccion_comercial: string;
  telefono: string;
  email: string;
  codigo_establecimiento: string;
  codigo_punto_venta: string;
  nombre_establecimiento: string | null;
  tipoestablecimiento: string;
  departamento: string;
  municipio: string;
  ambiente: string;
  tipo_documento: string;
  actividades_economicas: string[]; // Array de IDs de actividades económicas
}

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


export interface TipoGeneracionDocumentoInterface {
  id: number,
  codigo: string,
  descripcion: string
}

export interface TipoDTE {
  id: string;
  codigo: string;
  descripcion: string;
  version: number | null;
}

export interface TipoTributos {
  id: number,
  codigo: string,
  descripcion: string
}


export interface Tributos {
  id: number,
  codigo: string,
  descripcion: string,
  valor_tributo: string,
  tipo_tributo: number,
  tipo_valor: number
}

export interface ConfiguracionFacturaInterface {
  id: number,
  codigo: string,
  descripcion: string
}