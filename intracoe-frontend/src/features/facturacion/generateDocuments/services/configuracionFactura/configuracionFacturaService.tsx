import axios from 'axios';

const BASEURL = import.meta.env.VITE_URL_BASE;

export const getAllTipoDte = async () => {
  try {
    const response = await axios.get(`${BASEURL}/tipo-dte/`);
    return response.data;
  } catch (error) {
    throw new Error();
  }
};
