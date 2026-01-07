import React from 'react'
import sopraLogo from '../assets/logos/sopra-steria-logo.svg'

const SopraLogo = ({ className = "sopra-logo" }) => {
  return (
    <div className={className}>
      <img src={sopraLogo} alt="Sopra Steria" />
    </div>
  )
}

export default SopraLogo