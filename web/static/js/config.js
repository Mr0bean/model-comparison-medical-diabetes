// 环境配置文件
(function() {
    // 自动检测环境
    const hostname = window.location.hostname;
    const isProduction = hostname === 'ruan.etodo.top';

    // API 配置
    window.API_CONFIG = {
        BASE_URL: isProduction
            ? 'http://ruan.etodo.top/api'  // 生产环境
            : 'http://localhost:5001/api',  // 开发环境
        environment: isProduction ? 'production' : 'development'
    };

    console.log(`🌍 当前环境: ${window.API_CONFIG.environment}`);
    console.log(`🔗 API地址: ${window.API_CONFIG.BASE_URL}`);
})();
