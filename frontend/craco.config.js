const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      // Fix source-map-loader warnings for node_modules
      webpackConfig.module.rules = webpackConfig.module.rules.map(rule => {
        if (rule.enforce === 'pre' && rule.loader && rule.loader.includes('source-map-loader')) {
          return {
            ...rule,
            exclude: /node_modules/,
          };
        }
        return rule;
      });

      return webpackConfig;
    },
    devServer: (devServerConfig) => {
      // Remove deprecated middleware options entirely
      delete devServerConfig.onBeforeSetupMiddleware;
      delete devServerConfig.onAfterSetupMiddleware;
      
      return devServerConfig;
    },
  },
};
