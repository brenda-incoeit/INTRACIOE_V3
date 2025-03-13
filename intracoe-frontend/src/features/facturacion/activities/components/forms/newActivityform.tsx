import { useEffect, useState } from 'react';
import { Dialog } from 'primereact/dialog';
import React from 'react';
import { Select } from 'antd';
import { ActivitiesData } from '../../interfaces/activitiesData';
import styles from "../antdesignCustom.module.css"
import { MultiSelect, MultiSelectChangeEvent } from 'primereact/multiselect';
import "./antdesignCustom.module.css"


interface NewActivityProps {
    visible: boolean;
    setVisible: any;
}

interface activities {
    name: string;
    code: string;
}

export const NewActivityForm: React.FC<NewActivityProps> = ({
    visible,
    setVisible,
}) => {

    const [selectedActivities, setSelectedActivities] = useState<activities[]>([]);
    const activitiesList: activities[] = [
        { name: 'Transporte de pasajeros marítimo y de cabotaje', code: '50110' },
        { name: 'Venta al por menor de textiles y confecciones usados', code: '47742' },
        { name: 'Venta al por menor de medicamentos farmacéuticos y otros materiales y artículos de uso médico, odontológico y veterinario', code: '47721' },
        { name: 'Almacenes (venta de diversos artículos) ', code: '47119' },
        { name: 'Reparación y reconstrucción de vías, stop y otros artículos de fibra de vidrio', code: '45205' },
        { name: 'Venta al por menor de materiales de construcción, electrodomésticos, accesorios para autos y similares en puestos de feria y mercados ', code: '47895' }

    ];

    const handlerForm = (e: React.FormEvent) => {
        e.preventDefault();
        console.log("data: ",selectedActivities)
    };

    const selectHandler = (e: any) => {
        setSelectedActivities(e.value)
        console.log(e.value)
    }

    return (
        <>
            <Dialog
                header=<p className='px-5 font-bold text-xl'>Nueva actividad</p>
                visible={visible}
                style={{ width: '60vw' }}
                onHide={() => {
                    if (!visible) return;
                    setVisible(false);
                }}
            >
                <form className='flex flex-col gap-7 px-5'>
                    <span className='flex flex-col pt-5'>
                        <label htmlFor="code" className=''>Actividades economicas:</label>
                        <div className=" py-2 flex justify-content-center">
                            <MultiSelect value={selectedActivities} onChange={(e: MultiSelectChangeEvent) => { selectHandler(e) }} options={activitiesList} optionLabel="name"
                                filter placeholder="seleccionar actividad económica" className="w-full md:w-20rem" />
                        </div>
                        <div>
                            {selectedActivities.length > 0 && (
                                <div>
                                    <strong>Actividades seleccionadas:</strong>
                                    <ul>
                                        {selectedActivities.map((activities) => (
                                            <li key={activities.code} className='list-disc list-inside'>{activities.name}</li> // Muestra los nombres de las actividades seleccionadas
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </span>
                    <span className='flex gap-3 w-full justify-end '>
                        <button className='border border-primary-blue rounded-md text-primary-blue px-6 py-3 hover:cursor-pointer' onClick={() => setVisible(false)}>Cancelar</button>
                        <button className='bg-primary-blue text-white rounded-md px-6 py-3 hover:cursor-pointer' onClick={handlerForm}>Guardar</button>
                    </span>
                </form>
            </Dialog>
        </>
    );
};
