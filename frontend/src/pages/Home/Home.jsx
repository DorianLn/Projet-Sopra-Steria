import React from 'react'
import Navbar from '../../components/Navbar'
import HeroSection from '../../components/HeroSection'
import './Home.css'

const Home = () => {
    return (
        <div className="min-h-screen">
            <Navbar />
            <HeroSection />
        </div>
    )
}

export default Home