import React from 'react'
import Navbar from '../components/Navbar'
import HeroSection from '../components/HeroSection'
import CVUploader from '../components/CVUploader'

const Home = () => {
    return (
        <div className="min-h-screen bg-gray-50">
            <Navbar />
            <HeroSection />
            <CVUploader />
        </div>
    )
}

export default Home