import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home/Home';
import Start from './pages/Start/Start';
import HowItWorks from './pages/HowItWorks/HowItWorks';
import Example from './pages/Example/Example';
import './styles/index.css'


const App = () => {
  return (
      <div className='root'>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/start' element={<Start />} />
          <Route path='/howitworks' element={<HowItWorks />} />
          <Route path='/example' element={<Example />} />
        </Routes>
      </div>
  );
}

export default App; 
