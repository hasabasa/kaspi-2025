
import React from 'react';
import '@/styles/loading-animation.css';

const LoadingAnimation: React.FC = () => {
  return (
    <div className="loading-wrapper">
      <div className="box-wrap">
        <div className="box one"></div>
        <div className="box two"></div>
        <div className="box three"></div>
        <div className="box four"></div>
        <div className="box five"></div>
        <div className="box six"></div>
      </div>
    </div>
  );
};

export default LoadingAnimation;
