<template>
    <div class="app-container">
      <div class="container-fluid p-5 text-center app-header">
        <h1>Video Editor Online</h1>
      </div>
    </div>
</template>

<style>

.loader {
    border: 16px solid #f3f3f3;
    border-radius: 50%;
    border-top: 16px solid #3498db;
    width: 120px;
    height: 120px;
    -webkit-animation: spin 2s linear infinite; /* Safari */
    animation: spin 2s linear infinite;
  }
  
  /* Safari */
  @-webkit-keyframes spin {
    0% { -webkit-transform: rotate(0deg); }
    100% { -webkit-transform: rotate(360deg); }
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  video {
    width: 100%;
    height: auto;
    max-height: 500px;
  }
  
  .videodiv{
    padding: 10px;
    border: 2px solid #282860;
    border-radius: 10px;
  }
  .align-center{
    text-align: center;
  }
  
  @media (min-width: 1024px) {
    header {
      display: flex;
      place-items: center;
      padding-right: calc(var(--section-gap) / 2);
    }
  
    .logo {
      margin: 0 2rem 0 0;
    }
  
    header .wrapper {
      display: flex;
      place-items: flex-start;
      flex-wrap: wrap;
    }
}

.app-header {
    background-color: #9bc6db !important;
}

</style>