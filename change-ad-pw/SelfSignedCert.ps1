$SubjectName = [System.Net.Dns]::GetHostByName($env:computerName).HostName
$ValidDays = 1095

$name = New-Object -COM "X509Enrollment.CX500DistinguishedName.1"
$name.Encode("CN=$SubjectName", 0)

$key = New-Object -COM "X509Enrollment.CX509PrivateKey.1"
$key.ProviderName = "Microsoft RSA SChannel Cryptographic Provider"
$key.KeySpec = 1
$key.Length = 4096
$key.SecurityDescriptor = "D:PAI(A;;0xd01f01ff;;;SY)(A;;0xd01f01ff;;;BA)(A;;0x80120089;;;NS)"
$key.MachineContext = 1
$key.Create()

$cert = New-Object -COM "X509Enrollment.CX509CertificateRequestCertificate.1"
$cert.InitializeFromPrivateKey(2, $key, "")
$cert.Subject = $name
$cert.Issuer = $cert.Subject
$cert.NotBefore = (Get-Date).AddDays(-1)
$cert.NotAfter = $cert.NotBefore.AddDays($ValidDays)
$cert.Encode()

$enrollment = New-Object -COM "X509Enrollment.CX509Enrollment.1"
$enrollment.InitializeFromRequest($cert)
$certdata = $enrollment.CreateRequest(0)
$enrollment.InstallResponse(2, $certdata, 0, "")

$parsed_cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
$parsed_cert.Import([System.Text.Encoding]::UTF8.GetBytes($certdata))
$root_store = New-Object System.Security.Cryptography.X509Certificates.X509Store(
    [System.Security.Cryptography.X509Certificates.StoreName]::Root,
    "localmachine"
)
$root_store.Open("MaxAllowed")
$root_store.Add($parsed_cert)
$root_store.Close()
