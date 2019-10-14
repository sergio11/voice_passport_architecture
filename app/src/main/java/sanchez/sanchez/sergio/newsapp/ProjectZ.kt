package sanchez.sanchez.sergio.newsapp

import sanchez.sanchez.sergio.brownie.BrownieApp
import timber.log.Timber

class ProjectZ: BrownieApp() {

    override fun onDebugConfig() {
        super.onDebugConfig()
        Timber.plant(Timber.DebugTree())
    }

}