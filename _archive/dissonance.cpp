#include <iostream>
#include <fstream>
#include <cmath>
#include <vector>
using namespace std;

const int NUM_PARTIALS = 6;
const double PARTIAL_DECAY = 0.88;
const double SEMI_MULT = pow(2, 1./12); // semitone multiplier
const double SEMI_MULT_STEP = pow(SEMI_MULT, 1/10.);

int main() {
    vector<double> freq, partials, partials_ampl;
    freq.push_back(440); // A
    freq.push_back(440 * pow(SEMI_MULT, 4)); // 3rd
    freq.push_back(440 * pow(SEMI_MULT, 7)); // 5th

    for (int i = 0; i < freq.size(); ++i) {
        cout << "Frequency: " << freq[i] << endl;
        for (int j = 0; j < NUM_PARTIALS; ++j) {
            double f = freq[i] * (j + 1);
            double a = pow(PARTIAL_DECAY, j);
            partials.push_back(f);
            partials_ampl.push_back(a);
            cout << "  Partial: " << f << " @ " << a << endl;
        }
    }

    ofstream outfile("output.csv");
    for (double interval = 0.5; interval < 2 + 1e-7; interval *= SEMI_MULT_STEP)
    //for (double interval = 1.0; interval < 2 + 1e-7; interval *= SEMI_MULT_STEP)
    {
        double frequency = freq[0] * interval; // calculate dissonance for intervals from the root

        double dissonance = 0;
        double a_ampl = 1;
        for (int i = 0; i < NUM_PARTIALS; ++i) {
            double a_freq = frequency * (i + 1);
            for (int j = 0; j < partials.size(); ++j) {
                // calculate the dissonance between two partials
                double b_freq = partials[j];
                double b_ampl = partials_ampl[j];
                // fmin=min(a_freq, b_freq) base frequency is the lesser of (frequency * interval) and frequency
                // dstar=0.24 is interval of maximum dissonance, derived from a model of Plomp-Levelt dissonance curves for all frequencies
                // s1=0.0207 and s2=18.96 are used to stretch the curve so that its max dissonance occurs at dstar
                // If the point of maximum dissonance for a base frequency f occurs at dstar, then the dissonance between
                // f1 and f2 = amp1*amp2(e^-a1s[f2-f1] - e^-a2s[f2-f1]) where s = dstar/(s1*f1+f2)
                double s_dist = 0.24 * fabs(a_freq - b_freq) / (0.0207 * min(a_freq, b_freq) + 18.96); // the absolute diff between frequencies
                // A1=-3.51 and A2=-5.75 are values that determine the rates at which the function rises and falls
                // based on a gradient minimisation of the squared error between Plomp and Levelt's averaged data and the curve
                // C1=5 and C2=-5 are parameters with values to fit the experimental data of Plomp and Levelt

                double e = (exp(-3.51 * s_dist) - exp(-5.75 * s_dist));

                if (true) {
                    dissonance += min(a_ampl, b_ampl) * e;
                } else {
                    // http://www.acousticslab.org/learnmoresra/moremodel.html
                    double amp_max = max(a_ampl, b_ampl);
                    double amp_min = min(a_ampl, b_ampl);
                    double y = pow(amp_min * amp_max, 0.1) * 0.5 * pow(2 * amp_min / (amp_min + amp_max), 3.11);
                    dissonance += y * e;
                }
            }
            a_ampl *= PARTIAL_DECAY;
        }
        cout << "interval=" << interval << " frequency=" << frequency << " dissonance=" << dissonance << endl;
        outfile << interval << ',' << frequency << ',' << dissonance << endl;
    }//*/
    return 0;
}
