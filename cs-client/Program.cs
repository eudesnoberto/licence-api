using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace LicClient;

internal static class Program
{
    // Ajuste estes valores para apontar para o seu backend Flask
    private const string BaseUrl = "http://127.0.0.1:5000"; // em produção: https://www.fartgreen.fun
    private const string VerifyPath = "/verify";
    private const string ApiKey = "MINHA_API";              // igual API_KEY do .env da API
    private const string SharedSecret = "MEU_SEGREDO";      // igual SHARED_SECRET do .env da API

    // Versão do aplicativo protegido (apenas informativa para o servidor)
    private const string AppVersion = "1.0.0";

    private static int Main(string[] args)
    {
        try
        {
            var deviceId = DeviceId.GetOrCreate();

            Console.WriteLine($"[LicClient] DeviceId: {deviceId}");

            var (ok, response, msg) = VerifyLicenseAsync(deviceId, AppVersion).GetAwaiter().GetResult();

            if (!ok)
            {
                Console.Error.WriteLine($"[LicClient] Falha ao contatar servidor: {msg}");
                return 2; // erro técnico
            }

            Console.WriteLine($"[LicClient] allow={response.Allow}, msg={response.Msg}");

            if (!response.Allow)
            {
                // Licença não permitida
                return 1;
            }

            if (response.LicenseToken is { } token)
            {
                LicenseFile.Save(token);
            }

            // Aqui você pode iniciar o seu app principal (Process.Start) se quiser.
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("[LicClient] Erro inesperado: " + ex);
            return 3;
        }
    }

    private static async Task<(bool Ok, VerifyResponse Response, string Error)> VerifyLicenseAsync(string deviceId, string appVersion)
    {
        using var client = new HttpClient
        {
            Timeout = TimeSpan.FromSeconds(8)
        };

        var ts = DateTime.UtcNow.ToString("yyyyMMddHHmmss");
        var sigPayload = $"{deviceId}|{appVersion}|{ts}|{SharedSecret}";
        var sig = Sha256Hex(sigPayload);

        var query = new Dictionary<string, string?>
        {
            ["id"] = deviceId,
            ["version"] = appVersion,
            ["ts"] = ts,
            ["sig"] = sig,
            ["api_key"] = ApiKey
        };

        var url = BuildUrl(BaseUrl, VerifyPath, query);

        try
        {
            using var req = new HttpRequestMessage(HttpMethod.Get, url);
            if (!string.IsNullOrEmpty(ApiKey))
            {
                req.Headers.Add("X-API-Key", ApiKey);
            }

            using var resp = await client.SendAsync(req);
            var body = await resp.Content.ReadAsStringAsync();

            if (!resp.IsSuccessStatusCode)
            {
                return (false, new VerifyResponse(), $"HTTP {(int)resp.StatusCode}: {body}");
            }

            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };
            var parsed = JsonSerializer.Deserialize<VerifyResponse>(body, options);
            if (parsed is null)
            {
                return (false, new VerifyResponse(), "JSON inválido");
            }

            return (true, parsed, "");
        }
        catch (Exception ex)
        {
            return (false, new VerifyResponse(), ex.Message);
        }
    }

    private static string Sha256Hex(string input)
    {
        using var sha = SHA256.Create();
        var bytes = Encoding.UTF8.GetBytes(input);
        var hash = sha.ComputeHash(bytes);
        var sb = new StringBuilder(hash.Length * 2);
        foreach (var b in hash)
            sb.Append(b.ToString("x2"));
        return sb.ToString();
    }

    private static string BuildUrl(string baseUrl, string path, IDictionary<string, string?> query)
    {
        if (baseUrl.EndsWith("/"))
            baseUrl = baseUrl.TrimEnd('/');
        if (!path.StartsWith("/"))
            path = "/" + path;

        var qs = string.Join("&",
            query
                .Where(kv => kv.Value is not null)
                .Select(kv => $"{Uri.EscapeDataString(kv.Key)}={Uri.EscapeDataString(kv.Value!)}"));

        return $"{baseUrl}{path}?{qs}";
    }
}

internal static class DeviceId
{
    public static string GetOrCreate()
    {
        var filePath = GetFilePath();

        if (File.Exists(filePath))
        {
            var existing = File.ReadAllText(filePath).Trim();
            if (!string.IsNullOrWhiteSpace(existing))
                return existing;
        }

        var id = Guid.NewGuid().ToString("N"); // 32 chars hex
        Directory.CreateDirectory(Path.GetDirectoryName(filePath)!);
        File.WriteAllText(filePath, id);
        return id;
    }

    private static string GetFilePath()
    {
        var programData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        var dir = Path.Combine(programData, "MyApp");
        return Path.Combine(dir, "device.id");
    }
}

internal sealed class VerifyResponse
{
    public bool Allow { get; set; }
    public string Msg { get; set; } = "";
    public VerifyConfig Config { get; set; } = new();
    public LicenseToken? LicenseToken { get; set; }
}

internal sealed class VerifyConfig
{
    public int Interval { get; set; }
    public string[] Features { get; set; } = Array.Empty<string>();
    public string Message { get; set; } = "";
    public string? License_Expires_At { get; set; }
}

internal sealed class LicenseToken
{
    // Mapeia para "payload" (objeto com dados da licença)
    public JsonElement Payload { get; set; }

    // JSON bruto usado na assinatura HMAC (campo "payload_raw" no backend)
    public string Payload_Raw { get; set; } = "";

    public string Signature { get; set; } = "";
}

internal static class LicenseFile
{
    private static readonly string LicensePath;

    static LicenseFile()
    {
        var programData = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData);
        var dir = Path.Combine(programData, "MyApp");
        Directory.CreateDirectory(dir);
        LicensePath = Path.Combine(dir, "license.lic");
    }

    public static void Save(LicenseToken token)
    {
        try
        {
            var json = JsonSerializer.Serialize(token, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(LicensePath, json, Encoding.UTF8);
            Console.WriteLine($"[LicClient] Arquivo de licença salvo em {LicensePath}");
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine("[LicClient] Falha ao salvar arquivo de licença: " + ex.Message);
        }
    }
}