chrome.webNavigation.onCompleted.addListener(function(details){
  chrome.tabs.get(details.tabId, function(tab){
    if(!tab || !tab.url) return;
    // naive detection — send URL to native host
    const msg = {trigger:'openSensitiveUrl', url: tab.url};
    chrome.runtime.sendNativeMessage('com.dpsos.nativehost', msg, function(resp){
      // handle response
    });
  });
});