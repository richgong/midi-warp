#include <iostream>
#include <fstream>
#include <cmath>
using namespace std;


int main() {
    cout << "Enter the number of partials: ";
    int numpartials;
    cin >> numpartials;

    float frequ[1024];
    for (int i = 1; i <= numpartials; ++i) {
        cout << i << ") Enter frequency: ";
        cin >> frequ[i];
    }

    ofstream outfile("output.csv");
    for (float interval = 0.4; interval <= 2.3; interval += 0.01) {
        
        // fill allpartialsatinterval array with each element of freq array multiplied by interval.
        float allpartialsatinterval[1024];
        for (int k = 1; k <= numpartials; k++)
            allpartialsatinterval[k] = interval * frequ[k];
        
        float d = 0;
        // Calculate the dissonance between frequ[i] and interval*frequ[j]
        for (int i = 1; i <= numpartials; i++) {
            for (int j = 1; j <= numpartials; j++) {
                // fmin takes on the lesser of freq*1.x and frequ
                float fmin = min(frequ[i], allpartialsatinterval[j]); 

                const float S1 = 0.0207; // s1 and s2 are used to allow a single functional form to interpolate beween
                const float S2 = 18.96;  // the various P&L curves of different frequencies by sliding, stretching/compressing
                                         // the curve so that its max dissonance occurs at dstar. A least-square-fit was made
                                         // to determine the values.
                const float DSTAR = 0.24; // this is the point of maximum dissonance - the value is derived from a model of the Plomp-Levelt dissonance  curves for all frequencies.
                float s = DSTAR / (S1 * fmin + S2); // define s with interpolating values s1 and s2.
                // If the point of maximum dissonance for a base frequency f occurs at dstar, then the dissonance between
                // f1 with amp1 and f2 with amp2, is - amp1*amp2(e^-a1s[f2-f1] - e^-a2s[f2-f1]) where s = dstar/(s1f1+f2).....

                // the absolute diff between frequencies
                float fdif = fabs(allpartialsatinterval[j] - frequ[i]);
                const float A1 = -3.51; // theses values determine the rates at which the function rises and falls and
                const float A2 = -5.75; // and are based on a gradient minimisation of the squared error between Plomp and Levelt's averaged data and the curve
                const float C1 = 5, C2 = -5; // these parameters have values to fit the experimental data of Plomp and Levelt
                float dnew = (C1 * exp(A1 * s * fdif) + C2 * exp(A2 * s * fdif));
                d = d + dnew; // keep adding the dissonances of each loop, where d iterates the dissonance of 1 partial(frequ[i]) with
                              // each(all) of the timbre's other partials as they'd be at the current interval. This is done for
                              // for each partial(freq[i]) and every interval.
            }
        }
        cout << "interval=" << interval << " dissonance=" << d << endl;
        outfile << interval << ',' << d << endl;
    }
    return 0;
}
