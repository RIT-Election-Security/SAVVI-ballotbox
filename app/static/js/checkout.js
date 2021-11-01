function copy_element_text_by_id(element_id) {
    var text = document.getElementById(element_id);
    navigator.clipboard.writeText(text.innerText);
}

function download_receipt_as_file() {
    let verification_code = document.getElementById('receipt-verification-code').innerText
    let timestamp = document.getElementById('receipt-timestamp').innerText
    var text = "Verification Code: " + verification_code + "\nTime Cast: " + timestamp;
    var file_name = verification_code + "-receipt-.txt"
    download_text_as_file(text, file_name);
}

function download_text_as_file(text, filename) {
    var element = document.createElement("a");
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}
